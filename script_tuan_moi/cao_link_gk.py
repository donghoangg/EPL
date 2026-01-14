import os
import re
import time
import pandas as pd
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# =============================================================================
# CONFIG - CẤU HÌNH
# =============================================================================
# 1. Mùa giải cần cào (chỉ cần nhập năm bắt đầu)
SEASON_YEAR = 2025

# 2. Đường dẫn đến thư mục để lưu file Excel của thủ môn
# THAY ĐỔI: Đường dẫn được cập nhật theo yêu cầu của bạn
OUTPUT_DIR = r"E:\project 1\data_2025_2026\link_matchlog"

# 3. Đường dẫn file log
LOG_FILENAME = r"E:\project 1\log\link_matchlog_gk.txt"

# 4. Định nghĩa các loại chỉ số
# THAY ĐỔI: Chỉ giữ lại 'goalkeeper' vì chỉ cần lấy file này
CATEGORIES = {
    "goalkeeper": "keeper"
}

# 5. URL cơ sở
BASE_URL = "https://fbref.com"

# =============================================================================
# HÀM HỖ TRỢ
# =============================================================================

def load_existing_player_ids(filename):
    """
    Đọc file Excel và trả về một set các Player ID đã có để kiểm tra trùng lặp.
    """
    if not os.path.exists(filename):
        return set()
    try:
        # Thêm engine='openpyxl' để đảm bảo tương thích
        df_existing = pd.read_excel(filename, engine='openpyxl')
        if 'Player ID' in df_existing.columns:
            return set(df_existing['Player ID'].astype(str).tolist())
        return set()
    except Exception as e:
        print(f"[LỖI] Không thể đọc file '{filename}': {e}. Coi như chưa có ID nào.")
        return set()

def log_new_players(new_players_info, log_filename):
    """Ghi danh sách thủ môn mới cào được vào file log."""
    if not new_players_info:
        return

    log_dir = os.path.dirname(log_filename)
    os.makedirs(log_dir, exist_ok=True)

    today_str = datetime.now().strftime("%d/%m/%Y")
    
    print(f"\nĐang ghi log {len(new_players_info)} thủ môn mới vào file: {log_filename}")
    try:
        with open(log_filename, 'a', encoding='utf-8') as f:
            f.write(f"--- Thủ môn mới được thêm vào ngày {today_str} ---\n")
            for player in new_players_info:
                f.write(f"  - ID: {player['id']}, Tên: {player['name']}\n")
            f.write("\n")
        print("Ghi log thành công.")
    except Exception as e:
        print(f"[LỖI] Không thể ghi file log: {e}")

# =============================================================================
# HÀM CHÍNH
# =============================================================================

def generate_goalkeeper_matchlog_links(year):
    """
    Cào danh sách các THỦ MÔN mới, sau đó tạo và GHI TIẾP (APPEND) link matchlog
    vào file Excel 'link_goalkeeper'.
    """
    season_str = f"{year}-{year+1}"
    season_short = f"{str(year)[-2:]}{str(year+1)[-2:]}"
    
    # --- Bước 1: Tải danh sách Player ID đã tồn tại từ file output của thủ môn ---
    # THAY ĐỔI: Check ID trực tiếp từ file 'link_goalkeeper'
    goalkeeper_file_path = os.path.join(OUTPUT_DIR, f"link_goalkeeper_{season_short}.xlsx")
    existing_ids = load_existing_player_ids(goalkeeper_file_path)
    print(f"Kiểm tra file: {os.path.basename(goalkeeper_file_path)}")
    print(f"Đã tìm thấy {len(existing_ids)} Player ID thủ môn đã tồn tại.")

    # --- Bước 2: Lấy danh sách cầu thủ của mùa giải từ web ---
    print(f"\nBắt đầu lấy danh sách THỦ MÔN cho mùa giải {season_str} từ FBref...")
    
    new_players_info = []
    
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    url = f"{BASE_URL}/en/comps/9/{season_str}/stats/{season_str}-Premier-League-Stats"
    
    print(f"Đang truy cập URL: {url}")
    driver.get(url)
    time.sleep(3)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    comment_div = soup.find('div', {'id': 'all_stats_standard'})
    comment = comment_div.find(string=lambda text: isinstance(text, Comment))
    soup_comment = BeautifulSoup(comment, 'html.parser')
    table = soup_comment.find('table', {'id': 'stats_standard'})
    rows = table.find('tbody').find_all('tr')

    for row in rows:
        if row.has_attr('class') and 'thead' in row['class']:
            continue

        position_cell = row.find('td', {'data-stat': 'position'})
        
        if position_cell and 'GK' in position_cell.text:
            player_cell = row.find('td', {'data-stat': 'player'})
            if player_cell and player_cell.a:
                player_link = player_cell.a.get('href', "")
                match = re.search(r'/players/([^/]+)/', player_link)
                if match:
                    player_id = match.group(1)
                    if player_id in existing_ids:
                        continue
                    
                    player_name = player_cell.a.text
                    new_players_info.append({'id': player_id, 'name': player_name})
                    existing_ids.add(player_id)

    driver.quit()

    # --- Bước 3: Kiểm tra và ghi log nếu có thủ môn mới ---
    if not new_players_info:
        print("\nKhông có thủ môn mới nào được tìm thấy. Dừng chương trình.")
        return
        
    print(f"\nTìm thấy {len(new_players_info)} thủ môn mới.")
    log_new_players(new_players_info, LOG_FILENAME)

    # --- Bước 4: Tạo link và lưu file cho thủ môn ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\nFile sẽ được lưu/cập nhật tại: {OUTPUT_DIR}")

    # Vòng lặp này giờ chỉ chạy 1 lần cho 'goalkeeper'
    for file_prefix, url_category in CATEGORIES.items():
        print(f"  Đang xử lý loại chỉ số: '{file_prefix}'...")
        
        category_data = []
        for player in new_players_info:
            url_player_name = player['name'].replace(' ', '-')
            matchlog_link = (
                f"{BASE_URL}/en/players/{player['id']}/matchlogs/{season_str}/"
                f"{url_category}/{url_player_name}-Match-Logs"
            )
            category_data.append({
                'Player ID': player['id'],
                'Player': player['name'],
                'Season': season_str,
                'Link': matchlog_link
            })
            
        df_new = pd.DataFrame(category_data)
        # Tên file output bây giờ chính là file chúng ta đã kiểm tra ở Bước 1
        output_filename = goalkeeper_file_path

        if os.path.exists(output_filename):
            print(f"    -> File '{os.path.basename(output_filename)}' đã tồn tại. Đang thêm dữ liệu mới...")
            df_old = pd.read_excel(output_filename, engine='openpyxl')
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_combined.to_excel(output_filename, index=False)
        else:
            print(f"    -> File '{os.path.basename(output_filename)}' chưa tồn tại. Đang tạo file mới...")
            df_new.to_excel(output_filename, index=False)
            
        print(f"    -> Đã xử lý xong file cho '{file_prefix}'.")

# =============================================================================
# ĐIỂM BẮT ĐẦU CHẠY CHƯƠNG TRÌNH
# =============================================================================

if __name__ == '__main__':
    generate_goalkeeper_matchlog_links(SEASON_YEAR)
    print("\nHoàn tất! File cho thủ môn đã được cập nhật thành công.")