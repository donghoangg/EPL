import pandas as pd
import numpy as np
import os
from datetime import datetime

# ==============================================================================
# 1. ĐỊNH NGHĨA CÁC ĐƯỜNG DẪN
# ==============================================================================
BASE_DIR = r"E:\project 1"

# File gốc mới (2025-2026)
player_matchlog_path = os.path.join(BASE_DIR, "data_2025_2026", "matchlog_2526", "players_standard_matchlogs.csv")

# Các file tham chiếu
match_processed_path = os.path.join(BASE_DIR, "data_clean", "match_processed.xlsx")
club_info_path = os.path.join(BASE_DIR, "data_clean", "club.xlsx")
season_info_path = os.path.join(BASE_DIR, "data_clean", "season.xlsx") # Cần file này để ánh xạ Season

# File kết quả (Master)
output_path = os.path.join(BASE_DIR, "data_clean", "Club_player_matchlog_final.xlsx")

# File Import (Chỉ chứa dữ liệu mới)
import_output_path = os.path.join(BASE_DIR, "data_2025_2026", "data_import", "Club_player_matchlogs_import.xlsx")

# File Log
log_path = os.path.join(BASE_DIR, "log", "Player_matchlog.txt")

os.makedirs(os.path.dirname(import_output_path), exist_ok=True)
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# ==============================================================================
# 2. CÁC HÀM HỖ TRỢ (Giữ nguyên)
# ==============================================================================
def clean_score(score):
    if not isinstance(score, str): return score
    cleaned = score.strip().replace('–', '-')
    try:
        p1, p2 = cleaned.split('-')
        if p1.isdigit() and p2.isdigit(): return cleaned
    except: return score
    return score

def flip_score(score):
    if not isinstance(score, str) or '-' not in score: return score
    p = score.split('-')
    if len(p) == 2 and p[0].isdigit() and p[1].isdigit():
        return f"{p[1]}-{p[0]}"
    return score

def clean_id_str(col):
    return col.astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

# ==============================================================================
# 3. XỬ LÝ DỮ LIỆU
# ==============================================================================
try:
    print("Đang tải dữ liệu...")
    df = pd.read_csv(player_matchlog_path, encoding='utf-8')
    match_df = pd.read_excel(match_processed_path)
    club_df = pd.read_excel(club_info_path)
    season_df = pd.read_excel(season_info_path)

    # Tạo dictionary để ánh xạ Tên -> ID
    club_map = dict(zip(club_df['Squad'], club_df['Club_ID']))
    season_map = dict(zip(season_df['Season'], season_df['Season_ID']))

    # --- BƯỚC 1: CHUẨN BỊ DỮ LIỆU TRONG DF (CSV) ĐỂ KHỚP VỚI FILE MATCH_PROCESSED ---
    print("Đang ánh xạ Tên sang ID để lấy Match_ID...")
    
    # Xác định tên đội bóng tạm thời từ Venue
    df['Home_Name'] = np.where(df['Venue'] == 'Home', df['Squad'], df['Opponent'])
    df['Away_Name'] = np.where(df['Venue'] == 'Home', df['Opponent'], df['Squad'])
    
    # ÁNH XẠ SANG ID (Để khớp với các cột ID trong match_processed.xlsx)
    df['Season'] = df['Season'].map(season_map)
    df['Home Team'] = df['Home_Name'].map(club_map)
    df['Away Team'] = df['Away_Name'].map(club_map)

    # Chuẩn hóa ngày tháng để merge
    match_df['Date'] = pd.to_datetime(match_df['Date']).dt.date
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # --- BƯỚC 2: MERGE LẤY MATCH_ID ---
    # Bây giờ Season, Home Team, Away Team ở cả 2 bảng đều là ID nên sẽ merge được
    merge_cols = ['Season', 'Date', 'Round', 'Home Team', 'Away Team']
    
    # Làm sạch bảng tham chiếu match_df
    match_df_clean = match_df.drop_duplicates(subset=merge_cols)
    
    df = df.merge(match_df_clean[['Match_ID'] + merge_cols], on=merge_cols, how='left')

    # --- BƯỚC 3: LẤY CLUB_ID (Dựa trên Squad của cầu thủ) ---
    print("Đang lấy Club_ID...")
    df = df.merge(club_df[['Squad', 'Club_ID']], on='Squad', how='left')

    # --- BƯỚC 4: TẠO CÁC CỘT ID ĐỊNH DANH ---
    print("Đang tạo các cột ID định danh...")
    
    # Loại bỏ các dòng thiếu thông tin quan trọng (không khớp được Match_ID hoặc Club_ID)
    initial_len = len(df)
    df = df.dropna(subset=['Match_ID', 'Club_ID', 'Player ID'])
    print(f"Đã loại bỏ {initial_len - len(df)} dòng không khớp được ID.")

    # Chuyển ID về dạng chuỗi sạch
    df['Match_ID'] = clean_id_str(df['Match_ID'])
    df['Club_ID'] = clean_id_str(df['Club_ID'])
    df['Player ID'] = clean_id_str(df['Player ID'])

    # Tạo các ID ghép
    df['Club_Player ID'] = df['Club_ID'] + '-' + df['Player ID']
    df['Club_player_matchlog_ID'] = df['Match_ID'] + df['Club_Player ID']

    # --- BƯỚC 5: KIỂM TRA TRÙNG LẶP VÀ TÁCH DỮ LIỆU MỚI ---
    final_cols = [
        "Club_player_matchlog_ID", 
        "Match_ID", 
        "Club_Player ID", 
        "Venue", 
        "Start", 
        "Pos", 
        "Min"
    ]
    
    current_process_df = df[final_cols].copy()

    if os.path.exists(output_path):
        print("Đang kiểm tra ID cũ trong file master...")
        existing_df = pd.read_excel(output_path)
        existing_ids = set(existing_df['Club_player_matchlog_ID'].astype(str).unique())
        
        # Lọc ra những dòng có ID chưa tồn tại trong Master
        new_records = current_process_df[~current_process_df['Club_player_matchlog_ID'].isin(existing_ids)]
        updated_master_df = pd.concat([existing_df, new_records], ignore_index=True)
    else:
        print("File master chưa tồn tại, tạo mới hoàn toàn.")
        new_records = current_process_df
        updated_master_df = current_process_df

    # --- BƯỚC 6: LƯU FILE VÀ GHI LOG ---
    num_new = len(new_records)

    if num_new > 0:
        updated_master_df.to_excel(output_path, index=False)
        new_records.to_excel(import_output_path, index=False)
        print(f"Đã thêm {num_new} bản ghi mới vào Master và file Import.")
    else:
        print("Không có dữ liệu mới để thêm.")

    # Ghi log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] - Added: {num_new} new IDs from {os.path.basename(player_matchlog_path)}\n")

    print("-" * 50)
    print(f"XỬ LÝ HOÀN TẤT!")
    print(f"Tổng số dòng trong Master: {len(updated_master_df)}")

except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")
    import traceback
    traceback.print_exc()