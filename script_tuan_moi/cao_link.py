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

# 2. Đường dẫn đến thư mục để lưu các file Excel
OUTPUT_DIR = r"E:\project 1\data_2025_2026\link_matchlog"

# 3. Đường dẫn file log
LOG_FILENAME = r"E:\project 1\log\link_matchlog.txt"

# 4. Định nghĩa các loại chỉ số và phần tương ứng trong URL
CATEGORIES = {
    "standard": "summary",
    "defend": "defense",
    "passing": "passing",
    "passtype": "passing_types",
    "possession": "possession",
    "gca": "gca"
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
        df_existing = pd.read_excel(filename)
        if 'Player ID' in df_existing.columns:
            return set(df_existing['Player ID'].astype(str).tolist())
        return set()
    except Exception as e:
        print(f"[LỖI] Không thể đọc file '{filename}': {e}. Coi như chưa có ID nào.")
        return set()

def log_new_players(new_players_info, log_filename):
    """Ghi danh sách cầu thủ mới cào được vào file log."""
    if not new_players_info:
        return

    log_dir = os.path.dirname(log_filename)
    os.makedirs(log_dir, exist_ok=True)

    today_str = datetime.now().strftime("%d/%m/%Y")
    
    print(f"\nĐang ghi log {len(new_players_info)} cầu thủ mới vào file: {log_filename}")
    try:
        with open(log_filename, 'a', encoding='utf-8') as f:
            f.write(f"--- Cầu thủ mới được thêm vào ngày {today_str} ---\n")
            for player in new_players_info:
                f.write(f"  - ID: {player['id']}, Tên: {player['name']}\n")
            f.write("\n")
        print("Ghi log thành công.")
    except Exception as e:
        print(f"[LỖI] Không thể ghi file log: {e}")

# =============================================================================
# HÀM CHÍNH
# =============================================================================

def generate_all_matchlog_links(year):
    """
    Cào danh sách cầu thủ mới, sau đó tạo và GHI TIẾP (APPEND) các link matchlog
    vào các file Excel tương ứng.
    """
    season_str = f"{year}-{year+1}"
    season_short = f"{str(year)[-2:]}{str(year+1)[-2:]}"
    
    # --- Bước 1: Tải danh sách Player ID đã tồn tại từ file standard ---
    # Chúng ta dùng file standard làm file "chuẩn" để kiểm tra.
    standard_file_path = os.path.join(OUTPUT_DIR, f"link_standard_{season_short}.xlsx")
    existing_ids = load_existing_player_ids(standard_file_path)
    print(f"Đã tìm thấy {len(existing_ids)} Player ID đã tồn tại trong file.")

    # --- Bước 2: Lấy danh sách cầu thủ của mùa giải từ web ---
    print(f"\nBắt đầu lấy danh sách cầu thủ cho mùa giải {season_str} từ FBref...")
    
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
    # ... (Phần xử lý comment và bảng giữ nguyên)
    comment = comment_div.find(string=lambda text: isinstance(text, Comment))
    soup_comment = BeautifulSoup(comment, 'html.parser')
    table = soup_comment.find('table', {'id': 'stats_standard'})
    rows = table.find('tbody').find_all('tr')

    for row in rows:
        if row.has_attr('class') and 'thead' in row['class']:
            continue

        player_cell = row.find('td', {'data-stat': 'player'})
        if player_cell and player_cell.a:
            player_link = player_cell.a.get('href', "")
            match = re.search(r'/players/([^/]+)/', player_link)
            if match:
                player_id = match.group(1)
                # >>> KIỂM TRA NẾU ID ĐÃ TỒN TẠI THÌ BỎ QUA <<<
                if player_id in existing_ids:
                    continue
                
                # Nếu là ID mới, thêm vào danh sách và thêm vào set `existing_ids`
                # để tránh thêm trùng lặp nếu cầu thủ xuất hiện 2 lần trong bảng
                player_name = player_cell.a.text
                new_players_info.append({'id': player_id, 'name': player_name})
                existing_ids.add(player_id) # Cập nhật set để không bị trùng

    driver.quit()

    # --- Bước 3: Kiểm tra và ghi log nếu có cầu thủ mới ---
    if not new_players_info:
        print("\nKhông có cầu thủ mới nào được tìm thấy. Dừng chương trình.")
        return
        
    print(f"\nTìm thấy {len(new_players_info)} cầu thủ mới.")
    log_new_players(new_players_info, LOG_FILENAME)

    # --- Bước 4: Tạo thư mục và lặp qua từng loại chỉ số để tạo link và lưu file ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\nCác file sẽ được lưu/cập nhật tại: {OUTPUT_DIR}")

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
        output_filename = os.path.join(OUTPUT_DIR, f"link_{file_prefix}_{season_short}.xlsx")

        # >>> LOGIC GHI ĐÈ HOẶC GHI TIẾP (APPEND) <<<
        if os.path.exists(output_filename):
            # Nếu file đã tồn tại, đọc file cũ và nối dữ liệu mới vào
            print(f"    -> File '{os.path.basename(output_filename)}' đã tồn tại. Đang thêm dữ liệu mới...")
            df_old = pd.read_excel(output_filename)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_combined.to_excel(output_filename, index=False)
        else:
            # Nếu file chưa tồn tại, tạo file mới
            print(f"    -> File '{os.path.basename(output_filename)}' chưa tồn tại. Đang tạo file mới...")
            df_new.to_excel(output_filename, index=False)
            
        print(f"    -> Đã xử lý xong file cho '{file_prefix}'.")

# =============================================================================
# ĐIỂM BẮT ĐẦU CHẠY CHƯƠG TRÌNH
# =============================================================================

if __name__ == '__main__':
    generate_all_matchlog_links(SEASON_YEAR)
    print("\nHoàn tất! Tất cả các file đã được cập nhật thành công.")