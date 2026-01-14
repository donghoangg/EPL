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
from datetime import datetime  # THÊM MỚI: Để lấy ngày giờ

# --- CẤU HÌNH ---
INPUT_EXCEL_PATH = r"E:\project 1\data_2025_2026\link_matchlog\link_goalkeeper_2526.xlsx" 
OUTPUT_FOLDER = r"E:\project 1\data_2025_2026\matchlog_2526"
OUTPUT_CSV_PATH = os.path.join(OUTPUT_FOLDER, 'player_goalkeeper_matchlogs.csv')

# THÊM MỚI: Đường dẫn file log
LOG_FILE_PATH = r"E:\project 1\log\goalkeeper_matchlog.txt"

# --- THIẾT LẬP SELENIUM ---
options = webdriver.ChromeOptions()
options.add_argument('--headless') 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')

# --- HÀM ĐỂ CÀO VÀ XỬ LÝ DỮ LIỆU TỪ MỘT URL ---
def scrape_and_process_url(driver, url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        table_element = wait.until(
            EC.presence_of_element_located((By.ID, 'matchlogs_all'))
        )
        table_html = table_element.get_attribute('outerHTML')
        
        df = pd.read_html(table_html, header=1)[0]
        
        # Lọc bỏ dự bị không thi đấu và chỉ lấy Premier League
        df = df[~df['Pos'].str.contains('On matchday squad, but did not play', na=False)].copy()
        df = df[df['Comp'] == 'Premier League'].copy()
        
        # CHỈNH SỬA: Chỉ lấy 2 dòng cuối
        df = df.tail(2)
        
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
            
        return df
    except Exception as e:
        print(f"    Lỗi khi xử lý {url}: {type(e).__name__}")
        return None

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    try:
        source_df = pd.read_excel(INPUT_EXCEL_PATH)
        print(f"Đã đọc thành công file '{INPUT_EXCEL_PATH}' với {len(source_df)} thủ môn.")
    except Exception as e:
        print(f"Lỗi khi đọc file Excel: {e}")
        exit()

    all_matchlogs_list = []
    success_count = 0  # Biến đếm số thủ môn thành công
    driver = None

    try:
        print("\nĐang khởi tạo trình duyệt...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        for index, row in source_df.iterrows():
            player_name = row['Player']
            season = row['Season']
            matchlog_link = row['Link']
            
            print(f"\nĐang xử lý {index + 1}/{len(source_df)}: {player_name}")
            
            player_df = scrape_and_process_url(driver, matchlog_link)
            
            if player_df is not None and not player_df.empty:
                player_df.insert(0, 'Season', season)
                player_df.insert(0, 'Player', player_name)
                all_matchlogs_list.append(player_df)
                success_count += 1 # Tăng biến đếm khi thành công
                print(f"    -> Thành công: Lấy {len(player_df)} trận gần nhất.")
            else:
                print(f"    -> Bỏ qua: Không có dữ liệu phù hợp.")

            time.sleep(random.uniform(1, 2))

    finally:
        if driver:
            driver.quit()
            print("\nĐã đóng trình duyệt.")

    # Tổng hợp và lưu kết quả CSV
    if all_matchlogs_list:
        final_df = pd.concat(all_matchlogs_list, ignore_index=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        final_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
        print(f"\nĐã lưu dữ liệu vào: {OUTPUT_CSV_PATH}")
    
    # --- PHẦN GHI LOG (THÊM MỚI) ---
    try:
        # Tạo thư mục log nếu chưa có
        log_dir = os.path.dirname(LOG_FILE_PATH)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"Ngày cào: {current_time} - Số thủ môn cào thành công: {success_count}/{len(source_df)}\n"
        
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_message)
        
        print(f"Đã ghi log vào: {LOG_FILE_PATH}")
    except Exception as e:
        print(f"Lỗi khi ghi log: {e}")

    print(f"\n--- HOÀN TẤT! ---")