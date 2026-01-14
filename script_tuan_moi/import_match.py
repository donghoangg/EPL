import pandas as pd
from sqlalchemy import create_engine
import urllib

# 1. Thông tin kết nối (Giữ nguyên cấu hình của bạn)
server = r'LAP-CUA-HOANGGG\DONGHOANG'
database = 'EPL1'
username = 'sa'
password = '*********' # <-- Thay mật khẩu của bạn vào đây
driver = '{ODBC Driver 17 for SQL Server}' 

params = urllib.parse.quote_plus(
    f'DRIVER={driver};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

try:
    # 2. Đọc file Excel match_processed
    file_path = r"E:\project 1\data_2025_2026\data_import\match_import.xlsx"
    df = pd.read_excel(file_path)

    # 3. Đổi tên các cột theo yêu cầu trong ảnh
    column_mapping = {
        'Match_ID': 'Match_ID',
        'Season': 'Season_ID',      # Đổi Season -> Season_ID
        'Date': 'Date_played',      # Đổi Date -> Date_played
        'Round': 'Round_played',    # Đổi Round -> Round_played
        'Home Team': 'Home_team',   # Đổi Home Team -> Home_team
        'Away Team': 'Away_team',   # Đổi Away Team -> Away_team
        'Result': 'Result',
        'Score': 'Score'
    }
    
    df = df.rename(columns=column_mapping)

    # 4. Xử lý định dạng ngày tháng cho cột Date_played
    # Đảm bảo dữ liệu ngày tháng chuẩn để SQL không báo lỗi
    df['Date_played'] = pd.to_datetime(df['Date_played'], errors='coerce')

    # 5. Lọc lấy đúng các cột cần thiết theo thứ tự database
    cols_to_keep = [
        'Match_ID', 'Season_ID', 'Date_played', 'Round_played', 
        'Home_team', 'Away_team', 'Result', 'Score'
    ]
    df = df[cols_to_keep]

    # 6. Import vào bảng 'Matches'
    df.to_sql(name='Matches', con=engine, if_exists='append', index=False)

    print("Import dữ liệu vào bảng Matches thành công!")

except Exception as e:
    print(f"Lỗi: {e}")