import pandas as pd
from sqlalchemy import create_engine
import urllib

# 1. Thông tin kết nối
server = r'LAP-CUA-HOANGGG\DONGHOANG'
database = 'EPL1'
username = 'sa'
password = '********' 
driver = '{ODBC Driver 17 for SQL Server}' 

params = urllib.parse.quote_plus(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};')
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# 2. Hàm xử lý Import chung
def import_player_data(file_path, table_name, mapping):
    try:
        print(f"\n--- Đang xử lý bảng: {table_name} ---")
        df = pd.read_excel(file_path)
        
        # Đổi tên cột
        df = df.rename(columns=mapping)
        
        # Xóa trùng ID trong file Excel
        df = df.drop_duplicates(subset=['Club_player_matchlog_ID'], keep='first')
        
        # Lọc Khóa ngoại: Chỉ giữ lại ID đã có trong bảng Player_Match_log
        valid_log_ids = pd.read_sql("SELECT Club_player_matchlog_ID FROM Player_Match_log", engine)['Club_player_matchlog_ID'].tolist()
        df = df[df['Club_player_matchlog_ID'].isin(valid_log_ids)]
        
        # Lọc Trùng Khóa chính: Bỏ qua những dòng đã có trong bảng đích
        try:
            existing_ids = pd.read_sql(f"SELECT Club_player_matchlog_ID FROM {table_name}", engine)['Club_player_matchlog_ID'].tolist()
            df = df[~df['Club_player_matchlog_ID'].isin(existing_ids)]
        except:
            pass # Nếu bảng chưa có dữ liệu hoặc chưa tạo thì bỏ qua bước này
            
        if not df.empty:
            # Chỉ lấy các cột có trong mapping (để khớp với database)
            df = df[list(mapping.values())]
            df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
            print(f"Thành công: Đã nạp {len(df)} dòng vào {table_name}.")
        else:
            print(f"Thông báo: Không có dữ liệu mới hợp lệ cho {table_name}.")
            
    except Exception as e:
        print(f"Lỗi tại bảng {table_name}: {e}")

# 3. Định nghĩa Mapping cho từng bảng (Dựa theo ảnh bạn gửi)

# --- 1. Player_Matchlog_Defend ---
map_defend = {
    'Club_player_matchlog_ID': 'Club_player_matchlog_ID', 'Tkl': 'Num_of_tackle', 'TklW': 'Tackle_when_won_poss',
    'Def 3rd': 'Tackle_in_def', 'Mid 3rd': 'Tackle_in_mid', 'Att 3rd': 'Tackle_in_att', 'Tkl.1': 'Dribblers_tackled',
    'Att': 'Tackle_challenges', 'Tkl%': 'Per_of_dribblers_tackled', 'Lost': 'Tackle_lost', 'Blocks': 'Num_blocks',
    'Sh': 'Shot_block', 'Pass': 'Pass_block', 'Int': 'Interceptions', 'Tkl+Int': 'Tackle_and_Interception',
    'Clr': 'Clearances', 'Err': 'Error'
}

# --- 2. Player_Matchlog_gca ---
map_gca = {
    'Club_player_matchlog_ID': 'Club_player_matchlog_ID', 'SCA': 'SCA', 'PassLive': 'SCA_PassLive', 'PassDead': 'SCA_PassDead',
    'TO': 'SCA_TO', 'Sh': 'SCA_Shot', 'Fld': 'SCA_Fouled', 'Def': 'SCA_Defense', 'GCA': 'GCA',
    'PassLive.1': 'GCA_PassLive', 'PassDead.1': 'GCA_PassDead', 'TO.1': 'GCA_TO', 'Sh.1': 'GCA_Shot',
    'Fld.1': 'GCA_Fouled', 'Def.1': 'GCA_Defense'
}

# --- 3. Player_Matchlog_passtype ---
map_passtype = {
    'Club_player_matchlog_ID': 'Club_player_matchlog_ID', 'Att': 'Pass_Attempts', 'Live': 'Pass_Live', 'Dead': 'Pass_Dead',
    'FK': 'Pass_FK', 'TB': 'Pass_Through_Ball', 'Sw': 'Pass_Switch', 'Crs': 'Pass_Cross', 'TI': 'Pass_ThrowIn',
    'CK': 'Pass_Corner', 'In': 'Corner_In_Swing', 'Out': 'Corner_Out_Swing', 'Str': 'Corner_Straight',
    'Cmp': 'Pass_Completed', 'Off': 'Pass_Offside', 'Blocks': 'Pass_Blocked'
}

# --- 4. Player_Matchlog_passing ---
map_passing = {
    'Club_player_matchlog_ID': 'Club_player_matchlog_ID', 'Cmp': 'Pass_Completed_Total', 'Att': 'Pass_Attempted_Total',
    'Cmp%': 'Pass_Completion_Per_Total', 'TotDist': 'Total_Distance', 'PrgDist': 'Progressive_Distance',
    'Cmp.1': 'Pass_Completed_Short', 'Att.1': 'Pass_Attempted_Short', 'Cmp%.1': 'Pass_Completion_Per_Short',
    'Cmp.2': 'Pass_Completed_Medium', 'Att.2': 'Pass_Attempted_Medium', 'Cmp%.2': 'Pass_Completion_Per_Medium',
    'Cmp.3': 'Pass_Completed_Long', 'Att.3': 'Pass_Attempted_Long', 'Cmp%.3': 'Pass_Completion_Per_Long',
    'Ast': 'Assists', 'xAG': 'Expected_Assisted_Goals', 'xA': 'Expected_Assists', 'KP': 'Key_Passes',
    '1/3': 'Pass_to_Final_Third', 'PPA': 'Passes_into_Penalty_Area', 'CrsPA': 'Crosses_into_Penalty_Area', 'PrgP': 'Progressive_Passes'
}

# --- 5. Player_Matchlog_possession ---
map_possession = {
    'Club_player_matchlog_ID': 'Club_player_matchlog_ID', 'Touches': 'Total_Touches', 'Def Pen': 'Touches_Defensive_Penalty_Area',
    'Def 3rd': 'Touches_Defensive_Third', 'Mid 3rd': 'Touches_Middle_Third', 'Att 3rd': 'Touches_Attacking_Third',
    'Att Pen': 'Touches_Attacking_Penalty_Area', 'Live': 'Live_Ball_Touches', 'Att': 'Take_On_Attempts',
    'Succ': 'Take_Ons_Successful', 'Succ%': 'Take_Ons_Success_Percentage', 'Tkld': 'Tackled_During_Take_Ons',
    'Tkld%': 'Tackled_Percentage', 'Carries': 'Total_Carries', 'TotDist': 'Total_Carrying_Distance',
    'PrgDist': 'Progressive_Carrying_Distance', 'PrgC': 'Progressive_Carries', '1/3': 'Carries_Into_Final_Third',
    'CPA': 'Carries_Into_Penalty_Area', 'Mis': 'Miscontrols', 'Dis': 'Dispossessed', 'Rec': 'Passes_Received', 'PrgR': 'Progressive_Passes_Received'
}

# --- 6. Player_Matchlog_standard ---
map_standard = {
    'Club_player_matchlog_ID': 'Club_player_matchlog_ID', 'Gls': 'Goals', 'Ast': 'Assists', 'PK': 'Penalty_kicks_made',
    'PKatt': 'Penalty_kicks_attempted', 'Sh': 'Shot_total', 'SoT': 'Shot_on_target', 'CrdY': 'Yellow_Cards',
    'CrdR': 'Red_cards', 'Touches': 'Touches', 'Tkl': 'Tackles', 'Int': 'Interceptions', 'Blocks': 'Blocks',
    'xG': 'Expected_Goals', 'npxG': 'Non_penalty_Expected_Goals', 'xAG': 'Expected_Assisted_Goals',
    'SCA': 'Shot_creation', 'GCA': 'Goal_creation', 'Cmp': 'Pass_complete', 'Att': 'Pass_attemp',
    'Cmp%': 'Pass_completion', 'PrgP': 'Progressive_passes', 'Carries': 'Carries', 'PrgC': 'Progressive_carries',
    'Att.1': 'Take_on_attemp', 'Succ': 'Take_on_successful'
}

# --- 7. Player_Matchlog_goalkeeper ---
map_gk = {
    'Club_player_matchlog_ID': 'Club_player_matchlog_ID',
    'SoTA': 'Shots_on_Target_Against',
    'GA': 'Goals_Against',
    'Saves': 'Saves',
    'Save%': 'Save_Percentage',
    'CS': 'Clean_Sheets',
    'PSxG': 'Post_Shot_xG',
    'PKatt': 'PK_Attempted',
    'PKA': 'PK_Allowed',
    'PKsv': 'PK_Saved',
    'PKm': 'PK_Missed',
    'Cmp': 'Pass_Completed',
    'Att': 'Pass_Attempted',
    'Cmp%': 'Pass_Percentage',
    'Att (GK)': 'Pass_Attempted_GK',
    'Thr': 'Throws_Attempted',
    'Launch%': 'Launch_Percentage',
    'AvgLen': 'Avg_Pass_Length',
    'Att.1': 'Goal_Kicks_Attempted',
    'Launch%.1': 'Goal_Kick_Launch_Percentage',
    'AvgLen.1': 'Avg_Goal_Kick_Length',
    'Opp': 'Crosses_Faced',
    'Stp': 'Crosses_Stopped',
    'Stp%': 'Cross_Stop_Percentage',
    '#OPA': 'Def_Actions_Outside_PA',
    'AvgDist': 'Avg_Distance_Def_Actions'
}
# 4. Thực thi Import lần lượt
import_player_data(r"E:\project 1\data_2025_2026\data_import\defend_import.xlsx", "Player_Matchlog_Defend", map_defend)
import_player_data(r"E:\project 1\data_2025_2026\data_import\gca_import.xlsx", "Player_Matchlog_gca", map_gca)
import_player_data(r"E:\project 1\data_2025_2026\data_import\passtype_import.xlsx", "Player_Matchlog_passtype", map_passtype)
import_player_data(r"E:\project 1\data_2025_2026\data_import\passing_import.xlsx", "Player_Matchlog_passing", map_passing)
import_player_data(r"E:\project 1\data_2025_2026\data_import\possession_import.xlsx", "Player_Matchlog_possession", map_possession)
import_player_data(r"E:\project 1\data_2025_2026\data_import\standard_import.xlsx", "Player_Matchlog_standard", map_standard)
import_player_data(r"E:\project 1\data_2025_2026\data_import\goalkeeper_import.xlsx", "Player_Matchlog_goalkeeper", map_gk)

print("\n--- HOÀN THÀNH TẤT CẢ ---")