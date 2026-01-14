import pandas as pd
from sqlalchemy import create_engine
import urllib

# 1. Thông tin kết nối
server = r'LAP-CUA-HOANGGG\DONGHOANG'
database = 'EPL1'
username = 'sa'
password = '******' 
driver = '{ODBC Driver 17 for SQL Server}' 

params = urllib.parse.quote_plus(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};')
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

try:
    # 2. Đọc file Excel
    df = pd.read_excel(r"E:\project 1\data_2025_2026\data_import\Club_player_matchlogs_import.xlsx")

    # 3. Đổi tên các cột
    column_mapping = {
        'Club_player_matchlog_ID': 'Club_player_matchlog_ID',
        'Match_ID': 'Match_ID',
        'Club_Player ID': 'Club_player_ID',
        'Venue': 'Venue',
        'Start': 'Start',
        'Pos': 'Pos',
        'Min': 'Min_play'
    }
    df = df.rename(columns=column_mapping)

    # 4. Xử lý trùng ID ngay trong file Excel
    df = df.drop_duplicates(subset=['Club_player_matchlog_ID'], keep='first')

    # 5. LỌC DỮ LIỆU ĐỂ TRÁNH LỖI KHÓA NGOẠI (FOREIGN KEY)
    # Lấy danh sách ID cầu thủ và ID trận đấu ĐÃ CÓ trong database
    valid_club_players = pd.read_sql("SELECT Club_player_ID FROM Club_player", engine)['Club_player_ID'].tolist()
    valid_matches = pd.read_sql("SELECT Match_ID FROM Matches", engine)['Match_ID'].tolist()

    # Chỉ giữ lại những dòng mà Club_player_ID và Match_ID đã tồn tại trong SQL
    df_clean = df[
        df['Club_player_ID'].isin(valid_club_players) & 
        df['Match_ID'].isin(valid_matches)
    ]

    # 6. Xử lý trùng với dữ liệu đã có trong SQL (Incremental Load)
    existing_log_ids = pd.read_sql("SELECT Club_player_matchlog_ID FROM Player_Match_log", engine)['Club_player_matchlog_ID'].tolist()
    df_final = df_clean[~df_clean['Club_player_matchlog_ID'].isin(existing_log_ids)]

    # 7. Thông báo kết quả lọc
    print(f"Tổng số dòng trong file: {len(df)}")
    print(f"Số dòng bị loại bỏ do thiếu thông tin cầu thủ/trận đấu hoặc trùng: {len(df) - len(df_final)}")

    # 8. Import vào SQL
    if not df_final.empty:
        df_final.to_sql(name='Player_Match_log', con=engine, if_exists='append', index=False)
        print(f"Import thành công {len(df_final)} dòng vào bảng Player_Match_log!")
    else:
        print("Không có dữ liệu hợp lệ mới để import.")

except Exception as e:
    print(f"Lỗi: {e}")