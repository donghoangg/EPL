import pandas as pd
import numpy as np
import os
from datetime import datetime

# ==============================================================================
# 0. ĐỊNH NGHĨA CÁC ĐƯỜNG DẪN
# ==============================================================================
BASE_DIR = r"E:\project 1"

# Đường dẫn file input/output
raw_match_logs_path = os.path.join(BASE_DIR, "data_2025_2026", "matchlog_2526", "players_standard_matchlogs.csv")
final_processed_path = os.path.join(BASE_DIR, "data_clean", "match_processed.xlsx")
new_import_path = os.path.join(BASE_DIR, "data_2025_2026", "data_import", "match_import.xlsx")
log_file_path = os.path.join(BASE_DIR, "log", "match.txt")

# --- ĐƯỜNG DẪN FILE MAPPING (MỚI) ---
club_mapping_path = os.path.join(BASE_DIR, "data_clean", "club.xlsx")
season_mapping_path = os.path.join(BASE_DIR, "data_clean", "season.xlsx")

os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# ==============================================================================
# 1. CÁC HÀM HỖ TRỢ
# ==============================================================================
def clean_score(score):
    if not isinstance(score, str): return score
    cleaned = score.strip().replace('–', '-')
    try:
        p1, p2 = cleaned.split('-')
        if p1.isdigit() and p2.isdigit(): return cleaned
    except: return score
    month_map = {
        'JAN': '1', 'FEB': '2', 'MAR': '3', 'APR': '4', 'MAY': '5', 'JUN': '6',
        'JUL': '7', 'AUG': '8', 'SEP': '9', 'OCT': '10', 'NOV': '11', 'DEC': '12',
        'JANUARY': '1', 'FEBRUARY': '2', 'MARCH': '3', 'APRIL': '4', 'JUNE': '6',
        'JULY': '7', 'AUGUST': '8', 'SEPTEMBER': '9', 'OCTOBER': '10',
        'NOVEMBER': '11', 'DECEMBER': '12'
    }
    try:
        p1, p2 = cleaned.split('-')
        p1_up, p2_up = p1.upper(), p2.upper()
        if p1.isdigit() and p2_up in month_map: return f"{p1}-{month_map[p2_up]}"
        if p1_up in month_map and p2.isdigit():
            p2_num = p2.lstrip('0') or '0'
            return f"{month_map[p1_up]}-{p2_num}"
    except: pass
    return score

def flip_score(score):
    if not isinstance(score, str) or '-' not in score: return score
    p = score.split('-')
    if len(p) == 2 and p[0].isdigit() and p[1].isdigit():
        return f"{p[1]}-{p[0]}"
    return score

# ==============================================================================
# BẮT ĐẦU XỬ LÝ
# ==============================================================================
try:
    # 2. ĐỌC FILE MAPPING
    print("Đang tải dữ liệu mapping Club và Season...")
    df_club_map = pd.read_excel(club_mapping_path)
    df_season_map = pd.read_excel(season_mapping_path)
    
    club_dict = dict(zip(df_club_map['Squad'], df_club_map['Club_ID']))
    season_dict = dict(zip(df_season_map['Season'], df_season_map['Season_ID']))

    # 3. ĐỌC VÀ XỬ LÝ DỮ LIỆU THÔ
    print(f"Bắt đầu đọc file: {raw_match_logs_path}")
    df = pd.read_csv(raw_match_logs_path, encoding='utf-8')

    # Xác định tên đội bóng tạm thời
    df['Home_Name'] = np.where(df['Venue'] == 'Home', df['Squad'], df['Opponent'])
    df['Away_Name'] = np.where(df['Venue'] == 'Home', df['Opponent'], df['Squad'])

    # --- BƯỚC ÁNH XẠ VÀ LỌC (MỚI) ---
    df['Home Team'] = df['Home_Name'].map(club_dict)
    df['Away Team'] = df['Away_Name'].map(club_dict)
    df['Season'] = df['Season'].map(season_dict)

    # Loại bỏ các dòng không ánh xạ được ID (NaN)
    initial_len = len(df)
    df = df.dropna(subset=['Home Team', 'Away Team', 'Season'])
    dropped_count = initial_len - len(df)
    if dropped_count > 0:
        print(f"Cảnh báo: Đã loại bỏ {dropped_count} dòng do không tìm thấy Club_ID hoặc Season_ID tương ứng.")

    # Xử lý Result và Score
    result_split = df['Result'].str.split(' ', n=1, expand=True)
    df['Result_Letter'] = result_split[0]
    df['Score'] = result_split[1].apply(clean_score)

    result_map = {'W': 'L', 'L': 'W', 'D': 'D'}
    away_idx = df[df['Venue'] == 'Away'].index
    df.loc[away_idx, 'Score'] = df.loc[away_idx, 'Score'].apply(flip_score)
    df.loc[away_idx, 'Result_Letter'] = df.loc[away_idx, 'Result_Letter'].map(result_map)

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')
    
    unique_cols = ['Season', 'Round', 'Home Team', 'Away Team']
    df = df.drop_duplicates(subset=unique_cols, keep='first').reset_index(drop=True)

    new_data_df = df[['Season', 'Date', 'Round', 'Home Team', 'Away Team', 'Result_Letter', 'Score']]
    new_data_df = new_data_df.rename(columns={'Result_Letter': 'Result'})

    # 4. SO SÁNH VÀ CẬP NHẬT
    try:
        existing_df = pd.read_excel(final_processed_path)
        existing_df['Date'] = pd.to_datetime(existing_df['Date'])
    except FileNotFoundError:
        existing_df = pd.DataFrame()

    if not existing_df.empty:
        key_cols = ['Season', 'Round', 'Home Team', 'Away Team']
        merged = pd.merge(new_data_df, existing_df[key_cols], on=key_cols, how='left', indicator=True)
        truly_new_matches_df = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])
    else:
        truly_new_matches_df = new_data_df

    if truly_new_matches_df.empty:
        print("Không có trận đấu mới nào để cập nhật.")
    else:
        num_new_matches = len(truly_new_matches_df)
        print(f"Tìm thấy {num_new_matches} trận đấu mới.")

        # Kết hợp và tạo lại Match_ID
        if 'Match_ID' in existing_df.columns:
            existing_df = existing_df.drop(columns=['Match_ID'])
            
        combined_df = pd.concat([existing_df, truly_new_matches_df], ignore_index=True)
        combined_df = combined_df.sort_values(by=['Date', 'Home Team']).reset_index(drop=True)

        # Logic tạo Match_ID mới (Lấy năm từ Season_ID ví dụ SS2024 -> 2024)
        combined_df['Match_No'] = combined_df.groupby(['Season', 'Round']).cumcount() + 1
        combined_df['Round_No'] = combined_df['Round'].str.extract(r'(\d+)').astype(int)
        
        # Lấy 4 chữ số năm từ Season_ID
        combined_df['Year_Part'] = combined_df['Season'].str.extract(r'(\d{4})')
        
        combined_df['Match_ID'] = (
            "MATCH" + combined_df['Year_Part'] + "-" +
            combined_df['Round_No'].astype(str).str.zfill(2) + "-" +
            combined_df['Match_No'].astype(str).str.zfill(2)
        )
        
        final_cols = ['Match_ID', 'Season', 'Date', 'Round', 'Home Team', 'Away Team', 'Result', 'Score']
        combined_df = combined_df[final_cols]
        combined_df['Date'] = combined_df['Date'].dt.date

        # Lưu file và ghi log
        new_matches_with_id_df = combined_df.tail(num_new_matches)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] Da them {num_new_matches} tran. IDs: {', '.join(new_matches_with_id_df['Match_ID'].tolist())}\n")

        combined_df.to_excel(final_processed_path, index=False)
        new_matches_with_id_df.to_excel(new_import_path, index=False)
        print(f"Hoàn tất! Đã cập nhật {final_processed_path}")

except Exception as e:
    print(f"Lỗi: {e}")