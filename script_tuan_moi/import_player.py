import pandas as pd
from sqlalchemy import create_engine
import urllib

# --- PHẦN KẾT NỐI (Giữ nguyên như cũ) ---
server = r'LAP-CUA-HOANGGG\DONGHOANG'
database = 'EPL1'
username = 'sa'
password = '********' 
driver = '{ODBC Driver 17 for SQL Server}' 

params = urllib.parse.quote_plus(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};')
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

try:
    # 1. Đọc file
    df = pd.read_excel(r"E:\project 1\data_2025_2026\data_import\player_info_import.xlsx")

    # 2. Đổi tên cột
    column_mapping = {
        'Player ID': 'Player_ID',
        'Name': 'Player_name',
        'Born Date': 'DOB', # Cột ngày tháng
        'National Team': 'Nation',
        'Footed': 'Foot',
        'Height (cm)': 'Height',
        'Weight (kg)': 'Weight'
    }
    df = df.rename(columns=column_mapping)

    # 3. XỬ LÝ CỘT NGÀY THÁNG (QUAN TRỌNG NHẤT)
    # Chuyển đổi sang kiểu datetime của Python. 
    # errors='coerce' sẽ biến các ô trống hoặc lỗi thành NaT (Not a Time) - SQL Server sẽ hiểu là NULL.
    df['DOB'] = pd.to_datetime(df['DOB'], errors='coerce')

    # 4. Lọc các cột cần thiết
    cols_to_keep = ['Player_ID', 'Player_name', 'DOB', 'Nation', 'Foot', 'Height', 'Weight']
    df = df[cols_to_keep]

    # 5. Đẩy dữ liệu vào SQL Server
    # Lưu ý: Đảm bảo cột DOB trong SQL Server đang để kiểu dữ liệu là DATE hoặc DATETIME
    df.to_sql(name='Player', con=engine, if_exists='append', index=False)

    print("Import thành công! Các ô trống đã được chuyển thành NULL trong SQL.")

except Exception as e:
    print(f"Lỗi: {e}")