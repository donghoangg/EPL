"""
fbref_players_scraper_selenium_robust.py
Phiên bản: Tối ưu Selenium + Ghi đè file Import mới + Ghi thêm file Master.
"""

import time
import re
import sys
import traceback
import pandas as pd
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
from datetime import datetime

# -------- CONFIG --------
START_YEAR = 2022
END_YEAR = 2025
MAX_PLAYERS = None               
OUTPUT_FILENAME = r"E:\project 1\data_clean\player_info.xlsx"
LOG_FILENAME = r"E:\project 1\log\player_info.txt"
# ĐƯỜNG DẪN FILE IMPORT MỚI (Sẽ bị ghi đè mỗi lần có dữ liệu mới)
IMPORT_FILENAME = r"E:\project 1\data_2025_2026\data_import\player_info_import.xlsx"

RESTART_DRIVER_EVERY = 120       
SAFE_GET_RETRIES = 3
PAGE_LOAD_SLEEP = 1.5            
SEASON_COMP_URL_TEMPLATE = "{base}/en/comps/9/{season}/stats/{season}-Premier-League-Stats"
BASE_URL = "https://fbref.com"

# -------- CHROME OPTIONS & DRIVER MANAGEMENT --------
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def safe_get(driver, url, retries=SAFE_GET_RETRIES, wait_after=PAGE_LOAD_SLEEP):
    for attempt in range(1, retries + 1):
        try:
            driver.get(url)
            time.sleep(wait_after)
            return True
        except WebDriverException as e:
            print(f"  [safe_get] Lỗi khi tải (lần {attempt}/{retries}): {e}")
            time.sleep(2)
    return False

# -------- SCRAPING HELPERS --------
def parse_profile_soup(profile_html, player_id):
    soup = BeautifulSoup(profile_html, "html.parser")
    player_info = {"Player ID": player_id, 'Name': "N/A", 'Footed': "N/A", 'Height (cm)': "N/A",
                   'Weight (kg)': "N/A", 'Born Date': "N/A", 'National Team': "N/A"}
    try:
        meta_div = soup.find('div', {'id': 'meta'})
        if meta_div:
            h1 = meta_div.find('h1')
            if h1: player_info['Name'] = h1.get_text(strip=True)
            national_tag = meta_div.find('a', href=re.compile(r'/en/country/'))
            if national_tag: player_info['National Team'] = national_tag.get_text(strip=True)
            p_tags = meta_div.find_all('p')
            for p in p_tags:
                p_text = p.get_text(separator=' ', strip=True)
                if "Born:" in p_text:
                    born_span = p.find('span', {'id': 'necro-birth'})
                    if born_span and born_span.has_attr('data-birth'):
                        player_info['Born Date'] = born_span['data-birth']
                m_footed = re.search(r'Footed:\s*([A-Za-z]+)', p_text)
                if m_footed: player_info['Footed'] = m_footed.group(1)
                hmatch = re.search(r'(\d+)\s*cm', p_text)
                wmatch = re.search(r'(\d+)\s*kg', p_text)
                if hmatch: player_info['Height (cm)'] = hmatch.group(1)
                if wmatch: player_info['Weight (kg)'] = wmatch.group(1)
    except Exception as e:
        print(f"    [parse_profile_soup] Lỗi parse cho player {player_id}: {e}")
    return player_info

def get_player_profile_data_final_fix(driver, player_id, base_url=BASE_URL):
    profile_url = f"{base_url}/en/players/{player_id}/"
    if not safe_get(driver, profile_url):
        return {'Player ID': player_id, 'Name': 'N/A', 'Born Date': 'N/A', 'National Team': 'N/A',
                'Footed': 'N/A', 'Height (cm)': 'N/A', 'Weight (kg)': 'N/A'}
    return parse_profile_soup(driver.page_source, player_id)

def load_existing_player_ids(filename):
    if not os.path.exists(filename):
        return set()
    try:
        df_existing = pd.read_excel(filename)
        if 'Player ID' in df_existing.columns:
            return set(df_existing['Player ID'].astype(str).tolist())
    except Exception:
        pass
    return set()

# -------- CHÍNH: Lấy danh sách unique player profiles --------
def get_unique_player_profiles_only(start_year, end_year, max_players_to_scrape=None):
    unique_player_ids_found = load_existing_player_ids(OUTPUT_FILENAME)
    newly_scraped_profiles = []
    driver = None
    players_since_restart = 0

    try:
        driver = create_driver()
        for year in range(start_year, end_year + 1):
            if max_players_to_scrape is not None and len(newly_scraped_profiles) >= max_players_to_scrape:
                break
            season = f"{year}-{year+1}"
            url = SEASON_COMP_URL_TEMPLATE.format(base=BASE_URL, season=season)
            print(f"\n[SEASON] Đang xử lý mùa: {season}")
            if not safe_get(driver, url): continue

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            comment_div = soup.find('div', {'id': 'all_stats_standard'})
            if not comment_div: continue
            comment = comment_div.find(string=lambda text: isinstance(text, Comment))
            if not comment: continue
            soup_comment = BeautifulSoup(comment, 'html.parser')
            table = soup_comment.find('table', {'id': 'stats_standard'})
            if not table: continue

            rows = table.find('tbody').find_all('tr')
            for row in rows:
                if max_players_to_scrape is not None and len(newly_scraped_profiles) >= max_players_to_scrape:
                    break
                if row.has_attr('class') and 'thead' in row['class']: continue

                player_cell = row.find('td', {'data-stat': 'player'})
                if player_cell and player_cell.a:
                    player_link = player_cell.a.get('href', "")
                    m = re.search(r'/players/([^/]+)/', player_link)
                    if not m: continue
                    player_id = m.group(1)
                    if player_id in unique_player_ids_found: continue

                    if players_since_restart >= RESTART_DRIVER_EVERY:
                        driver.quit()
                        driver = create_driver()
                        players_since_restart = 0

                    print(f"  Cào mới: {player_id}...", end=" ")
                    profile_data = get_player_profile_data_final_fix(driver, player_id, BASE_URL)
                    print(f"Done: {profile_data.get('Name')}")

                    newly_scraped_profiles.append(profile_data)
                    unique_player_ids_found.add(player_id)
                    players_since_restart += 1
    except Exception as e:
        print("[ERROR]", e)
    finally:
        if driver: driver.quit()
    return pd.DataFrame(newly_scraped_profiles)

def log_newly_scraped_players(df_new, filename):
    if df_new.empty: return
    log_dir = os.path.dirname(filename)
    if not os.path.exists(log_dir): os.makedirs(log_dir)
    today_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"--- Cầu thủ mới ngày {today_str} ---\n")
        for _, row in df_new.iterrows():
            f.write(f"  - ID: {row['Player ID']}, Tên: {row['Name']}\n")
        f.write("\n")

# -------- MAIN --------
if __name__ == "__main__":
    df_new = get_unique_player_profiles_only(START_YEAR, END_YEAR, max_players_to_scrape=MAX_PLAYERS)

    if not df_new.empty:
        # 1. Ghi Log text
        log_newly_scraped_players(df_new, LOG_FILENAME)
        
        # 2. GHI ĐÈ VÀO FILE IMPORT (Chỉ chứa những cầu thủ vừa cào được)
        try:
            import_dir = os.path.dirname(IMPORT_FILENAME)
            if not os.path.exists(import_dir):
                os.makedirs(import_dir)
            df_new.to_excel(IMPORT_FILENAME, index=False)
            print(f"\n[SUCCESS] Đã ghi đè {len(df_new)} cầu thủ mới vào file IMPORT: {IMPORT_FILENAME}")
        except Exception as e:
            print(f"[ERROR] Không thể ghi file import: {e}")

        # 3. GHI THÊM VÀO FILE MASTER (Lưu trữ toàn bộ lịch sử)
        if os.path.exists(OUTPUT_FILENAME):
            df_old = pd.read_excel(OUTPUT_FILENAME)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_combined = df_new

        # Sắp xếp cột
        column_order = ['Player ID', 'Name', 'Born Date', 'National Team', 'Footed', 'Height (cm)', 'Weight (kg)']
        df_combined = df_combined[[c for c in column_order if c in df_combined.columns]]
        
        try:
            df_combined.to_excel(OUTPUT_FILENAME, index=False)
            print(f"[SUCCESS] Đã cập nhật file MASTER: {OUTPUT_FILENAME}")
        except Exception as e:
            print(f"[ERROR] Không thể ghi file master: {e}")
    else:
        print("\nKhông có cầu thủ mới nào để cập nhật.")