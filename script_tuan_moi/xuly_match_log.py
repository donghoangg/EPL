import pandas as pd
import numpy as np
import os
from datetime import datetime
import traceback

# ==============================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN VÀ THÔNG SỐ
# ==============================================================================
BASE_DIR = r"E:\project 1"
MATCH_REF_PATH = os.path.join(BASE_DIR, "data_clean", "match_processed.xlsx")
CLUB_REF_PATH = os.path.join(BASE_DIR, "data_clean", "club.xlsx")
SEASON_REF_PATH = os.path.join(BASE_DIR, "data_clean", "season.xlsx")
FINAL_LOG_PATH = os.path.join(BASE_DIR, "log", "match_log_import.txt")

CATEGORIES = {
    "Standard": {
        "input": "players_standard_matchlogs.csv",
        "master": "player_standard_matchlog.xlsx",
        "import": "standard_import.xlsx",
        "stats": ['Gls', 'Ast', 'PK', 'PKatt', 'Sh', 'SoT', 'CrdY', 'CrdR', 'Touches', 'Tkl', 'Int', 'Blocks', 'xG', 'npxG', 'xAG', 'SCA', 'GCA', 'Cmp', 'Att', 'Cmp%', 'PrgP', 'Carries', 'PrgC', 'Att.1', 'Succ']
    },
    "GCA": {
        "input": "all_gca_premier_league_matchlogs_final.csv",
        "master": "player_gca_matchlog.xlsx",
        "import": "gca_import.xlsx",
        "stats": ['SCA', 'PassLive', 'PassDead', 'TO', 'Sh', 'Fld', 'Def', 'GCA', 'PassLive.1', 'PassDead.1', 'TO.1', 'Sh.1', 'Fld.1', 'Def.1']
    },
    "Defend": {
        "input": "player_defensive_actions_matchlogs.csv",
        "master": "player_defensive_actions_matchlog.xlsx",
        "import": "defend_import.xlsx",
        "stats": ['Tkl', 'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl.1', 'Att', 'Tkl%', 'Lost', 'Blocks', 'Sh', 'Pass', 'Int', 'Tkl+Int', 'Clr', 'Err']
    },
    "PassType": {
        "input": "player_pass_types_matchlogs.csv",
        "master": "player_passtype_matchlog.xlsx",
        "import": "passtype_import.xlsx",
        "stats": ['Att', 'Live', 'Dead', 'FK', 'TB', 'Sw', 'Crs', 'TI', 'CK', 'In', 'Out', 'Str', 'Cmp', 'Off', 'Blocks']
    },
    "Passing": {
        "input": "player_passing_matchlogs.csv",
        "master": "player_passing_matchlog.xlsx",
        "import": "passing_import.xlsx",
        "stats": ['Cmp', 'Att', 'Cmp%', 'TotDist', 'PrgDist', 'Cmp.1', 'Att.1', 'Cmp%.1', 'Cmp.2', 'Att.2', 'Cmp%.2', 'Cmp.3', 'Att.3', 'Cmp%.3', 'Ast', 'xAG', 'xA', 'KP', '1/3', 'PPA', 'CrsPA', 'PrgP']
    },
    "Possession": {
        "input": "player_possession_matchlogs.csv",
        "master": "player_possession_matchlog.xlsx",
        "import": "possession_import.xlsx",
        "stats": ['Touches', 'Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att Pen', 'Live', 'Att', 'Succ', 'Succ%', 'Tkld', 'Tkld%', 'Carries', 'TotDist', 'PrgDist', 'PrgC', '1/3', 'CPA', 'Mis', 'Dis', 'Rec', 'PrgR']
    },
    "Goalkeeper": {
        "input": "player_goalkeeper_matchlogs.csv",
        "master": "player_goalkeeper_matchlog.xlsx",
        "import": "goalkeeper_import.xlsx",
        "stats": ['SoTA', 'GA', 'Saves', 'Save%', 'CS', 'PSxG', 'PKatt', 'PKA', 'PKsv', 'PKm', 'Cmp', 'Att', 'Cmp%', 'Att (GK)', 'Thr', 'Launch%', 'AvgLen', 'Att.1', 'Launch%.1', 'AvgLen.1', 'Opp', 'Stp', 'Stp%', '#OPA', 'AvgDist']
    }
}

# ==============================================================================
# 2. CÁC HÀM HỖ TRỢ
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
# 3. LOGIC XỬ LÝ CHÍNH
# ==============================================================================
def run_all_processes():
    log_results = []
    
    try:
        print("--- ĐANG TẢI DỮ LIỆU THAM CHIẾU ---")
        match_df = pd.read_excel(MATCH_REF_PATH)
        club_df = pd.read_excel(CLUB_REF_PATH)
        season_df = pd.read_excel(SEASON_REF_PATH)
        
        club_map = dict(zip(club_df['Squad'], club_df['Club_ID']))
        season_map = dict(zip(season_df['Season'], season_df['Season_ID']))

        match_df['Date'] = pd.to_datetime(match_df['Date']).dt.date
        match_df_clean = match_df.drop_duplicates(subset=['Season', 'Date', 'Round', 'Home Team', 'Away Team'])

        for cat_name, config in CATEGORIES.items():
            print(f"\n>>> Đang xử lý phần: {cat_name}")
            
            input_path = os.path.join(BASE_DIR, "data_2025_2026", "matchlog_2526", config["input"])
            master_path = os.path.join(BASE_DIR, "data_clean", config["master"])
            import_path = os.path.join(BASE_DIR, "data_2025_2026", "data_import", config["import"])
            
            if not os.path.exists(input_path):
                print(f"Bỏ qua {cat_name}: Không tìm thấy file input.")
                continue

            # 1. Đọc dữ liệu gốc và sửa lỗi tên cột Excel (1/3 bị đổi thành 3-Jan)
            df = pd.read_csv(input_path, encoding='utf-8')
            if '3-Jan' in df.columns:
                df = df.rename(columns={'3-Jan': '1/3'})

            # 2. Ánh xạ Tên sang ID để khớp với match_processed.xlsx
            df['Home_Name'] = np.where(df['Venue'] == 'Home', df['Squad'], df['Opponent'])
            df['Away_Name'] = np.where(df['Venue'] == 'Home', df['Opponent'], df['Squad'])
            
            df['Season'] = df['Season'].map(season_map)
            df['Home Team'] = df['Home_Name'].map(club_map)
            df['Away Team'] = df['Away_Name'].map(club_map)
            df['Date'] = pd.to_datetime(df['Date']).dt.date

            # 3. Merge lấy Match_ID và Club_ID
            merge_cols = ['Season', 'Date', 'Round', 'Home Team', 'Away Team']
            df = df.merge(match_df_clean[['Match_ID'] + merge_cols], on=merge_cols, how='left')
            df = df.merge(club_df[['Squad', 'Club_ID']], on='Squad', how='left')

            # 4. Tạo ID định danh
            df = df.dropna(subset=['Match_ID', 'Club_ID', 'Player ID'])
            df['Match_ID'] = clean_id_str(df['Match_ID'])
            df['Club_ID'] = clean_id_str(df['Club_ID'])
            df['Player ID'] = clean_id_str(df['Player ID'])
            df['Club_player_matchlog_ID'] = df['Match_ID'] + df['Club_ID'] + '-' + df['Player ID']

            # 5. Trích xuất stats (Sử dụng tên cột gốc từ CSV)
            existing_stats = [col for col in config["stats"] if col in df.columns]
            current_process_df = df[['Club_player_matchlog_ID'] + existing_stats].drop_duplicates()

            # 6. Kiểm tra trùng lặp với Master
            if os.path.exists(master_path):
                master_df = pd.read_excel(master_path)
                existing_ids = set(master_df['Club_player_matchlog_ID'].astype(str).unique())
                new_records = current_process_df[~current_process_df['Club_player_matchlog_ID'].isin(existing_ids)]
                updated_master_df = pd.concat([master_df, new_records], ignore_index=True)
            else:
                new_records = current_process_df
                updated_master_df = current_process_df
            
            num_new = len(new_records)

            # 7. Lưu file
            if num_new > 0:
                updated_master_df.to_excel(master_path, index=False)
                new_records.to_excel(import_path, index=False)
                print(f"Thành công: Thêm {num_new} ID mới.")
            else:
                print("Không có dữ liệu mới.")
            
            log_results.append(f"{cat_name}: {num_new}")

        # Ghi log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(FINAL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] - " + ", ".join(log_results) + "\n")
            
        print("\n" + "="*50 + "\nTẤT CẢ TIẾN TRÌNH HOÀN TẤT!")

    except Exception as e:
        print(f"\nLỖI HỆ THỐNG: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_all_processes()