import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os
from datetime import datetime

# --- CẤU HÌNH DANH SÁCH CÁC PHẦN CẦN CÀO ---
TASKS = [
    {
        "name": "Standard",
        "input": r"E:\project 1\data_2025_2026\link_matchlog\link_standard_2526.xlsx",
        "output": r"E:\project 1\data_2025_2026\matchlog_2526\players_standard_matchlogs.csv"
    },
    {
        "name": "Possession",
        "input": r"E:\project 1\data_2025_2026\link_matchlog\link_possession_2526.xlsx",
        "output": r"E:\project 1\data_2025_2026\matchlog_2526\player_possession_matchlogs.csv"
    },
    {
        "name": "Passing",
        "input": r"E:\project 1\data_2025_2026\link_matchlog\link_passing_2526.xlsx",
        "output": r"E:\project 1\data_2025_2026\matchlog_2526\player_passing_matchlogs.csv"
    },
    {
        "name": "Pass Type",
        "input": r"E:\project 1\data_2025_2026\link_matchlog\link_passtype_2526.xlsx",
        "output": r"E:\project 1\data_2025_2026\matchlog_2526\player_pass_types_matchlogs.csv"
    },
    {
        "name": "Defensive",
        "input": r"E:\project 1\data_2025_2026\link_matchlog\link_defend_2526.xlsx",
        "output": r"E:\project 1\data_2025_2026\matchlog_2526\player_defensive_actions_matchlogs.csv"
    },
    {
        "name": "GCA",
        "input": r"E:\project 1\data_2025_2026\link_matchlog\link_gca_2526.xlsx",
        "output": r"E:\project 1\data_2025_2026\matchlog_2526\all_gca_premier_league_matchlogs_final.csv"
    }
]

LOG_FILE_PATH = r"E:\project 1\log\scrapt_player_matchlog.txt"

# --- THIẾT LẬP SELENIUM ---
options = webdriver.ChromeOptions()
options.add_argument('--headless') 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')

def write_log(message):
    """Hàm ghi log vào file txt"""
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def scrape_and_process_url(driver, url):
    """Hàm cào và xử lý bảng dữ liệu"""
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        table_element = wait.until(EC.presence_of_element_located((By.ID, 'matchlogs_all')))
        table_html = table_element.get_attribute('outerHTML')
        
        df = pd.read_html(table_html, header=1)[0]
        
        # Lọc bỏ hàng không thi đấu và chỉ lấy Premier League
        df = df[~df['Pos'].str.contains('On matchday squad, but did not play', na=False)].copy()
        df = df[df['Comp'] == 'Premier League'].copy()
        
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
            
        return df
    except Exception:
        return None

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    driver = None
    try:
        print("Đang khởi tạo trình duyệt...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        for task in TASKS:
            task_name = task['name']
            input_path = task['input']
            output_path = task['output']
            
            print(f"\n=== ĐANG BẮT ĐẦU PHẦN: {task_name} ===")
            
            if not os.path.exists(input_path):
                print(f"Lỗi: Không tìm thấy file {input_path}")
                continue

            source_df = pd.read_excel(input_path)
            all_matchlogs_list = []
            success_count = 0

            for index, row in source_df.iterrows():
                player_id = row['Player ID']
                player_name = row['Player']
                season = row['Season']
                matchlog_link = row['Link']
                
                print(f"[{task_name}] {index + 1}/{len(source_df)}: {player_name}")
                
                player_df = scrape_and_process_url(driver, matchlog_link)
                
                if player_df is not None and not player_df.empty:
                    # LẤY DÒNG CUỐI CÙNG
                    player_df = player_df.tail(4)
                    
                    # CHÈN THÔNG TIN CẦU THỦ
                    player_df.insert(0, 'Season', season)
                    player_df.insert(0, 'Player', player_name)
                    player_df.insert(0, 'Player ID', player_id)
                    
                    all_matchlogs_list.append(player_df)
                    success_count += 1
                
                # Nghỉ ngẫu nhiên để tránh bị chặn
                time.sleep(random.uniform(0.5, 1))

            # Lưu kết quả của từng phần
            if all_matchlogs_list:
                final_df = pd.concat(all_matchlogs_list, ignore_index=True)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
                
                log_msg = f"Phần {task_name}: Cào thành công {success_count}/{len(source_df)} cầu thủ."
                print(f"-> {log_msg}")
                write_log(log_msg)
            else:
                write_log(f"Phần {task_name}: Không có dữ liệu nào được cào.")

    except Exception as e:
        print(f"Lỗi hệ thống: {e}")
        write_log(f"LỖI HỆ THỐNG: {str(e)}")
    
    finally:
        if driver:
            driver.quit()
            print("\nĐã đóng trình duyệt. Hoàn tất tất cả các phần.")