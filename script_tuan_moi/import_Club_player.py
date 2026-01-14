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
    # 2. Đọc file Excel Club_player
    file_path = r"E:\project 1\data_2025_2026\data_import\Club_player_import.xlsx"
    df = pd.read_excel(file_path)

    # 3. Đổi tên các cột theo yêu cầu trong ảnh
    # 'Tên trong file': 'Tên trong database'
    column_mapping = {
        'Club_Player ID': 'Club_player_ID',
        'Player ID': 'Player_ID',
        'Club_ID': 'Club_ID' # Cột này giữ nguyên nhưng viết lại cho chắc chắn
    }
    
    df = df.rename(columns=column_mapping)

    # 4. Lọc lấy đúng các cột cần thiết
    cols_to_keep = ['Club_player_ID', 'Player_ID', 'Club_ID']
    df = df[cols_to_keep]

    # 5. Import vào bảng 'Club_player'
    df.to_sql(name='Club_player', con=engine, if_exists='append', index=False)

    print("Import dữ liệu vào bảng Club_player thành công!")

except Exception as e:
    print(f"Lỗi: {e}")