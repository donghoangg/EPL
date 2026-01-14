import pandas as pd
import os
from datetime import datetime

# ==============================================================================
# 0. ĐỊNH NGHĨA CÁC ĐƯỜNG DẪN
# ==============================================================================
BASE_DIR = r"E:\project 1"

# Đường dẫn file input (Cập nhật theo yêu cầu mới)
match_logs_path = os.path.join(BASE_DIR, "data_2025_2026", "matchlog_2526", "players_standard_matchlogs.csv")
club_info_path = os.path.join(BASE_DIR, "data_clean", "club.xlsx")
player_info_path = os.path.join(BASE_DIR, "data_clean", "player_info.xlsx")

# Đường dẫn file output
master_path = os.path.join(BASE_DIR, "data_clean", "Club_player.xlsx")
import_path = os.path.join(BASE_DIR, "data_2025_2026", "data_import", "Club_player_import.xlsx")
log_path = os.path.join(BASE_DIR, "log", "Club_player.txt")

# Đảm bảo thư mục log và import tồn tại
os.makedirs(os.path.dirname(import_path), exist_ok=True)
os.makedirs(os.path.dirname(log_path), exist_ok=True)

print("Đã thiết lập các đường dẫn file.")

# ==============================================================================
# BẮT ĐẦU XỬ LÝ
# ==============================================================================
try:
    # 1. ĐỌC CÁC FILE DỮ LIỆU
    print(f"Đang đọc file match logs mới: {match_logs_path}")
    match_logs_df = pd.read_csv(match_logs_path)
    club_info_df = pd.read_excel(club_info_path)
    player_info_df = pd.read_excel(player_info_path)

    # 2. TRÍCH XUẤT CÁC CẶP (PLAYER, SQUAD) DUY NHẤT TỪ FILE MỚI
    new_pairs = match_logs_df[['Player', 'Squad']].drop_duplicates().reset_index(drop=True)

    # 3. MERGE ĐỂ LẤY ID
    # Lấy Club_ID
    new_pairs = pd.merge(new_pairs, club_info_df[['Squad', 'Club_ID']], on='Squad', how='left')
    # Lấy Player ID
    new_pairs = pd.merge(new_pairs, player_info_df[['Name', 'Player ID']], left_on='Player', right_on='Name', how='left')

    # Loại bỏ hàng thiếu ID
    new_pairs.dropna(subset=['Player ID', 'Club_ID'], inplace=True)

    # Tạo Club_Player ID
    new_pairs['Player ID'] = new_pairs['Player ID'].astype(str).str.replace('.0', '', regex=False)
    new_pairs['Club_ID'] = new_pairs['Club_ID'].astype(str).str.replace('.0', '', regex=False)
    new_pairs['Club_Player ID'] = new_pairs['Club_ID'] + '-' + new_pairs['Player ID']

    # Chuẩn bị DataFrame kết quả xử lý xong
    processed_df = new_pairs[['Club_Player ID', 'Player ID', 'Club_ID']].drop_duplicates()

    # 4. KIỂM TRA TRÙNG LẶP VỚI FILE HIỆN TẠI (MASTER)
    if os.path.exists(master_path):
        existing_master_df = pd.read_excel(master_path)
        existing_master_df['Club_Player ID'] = existing_master_df['Club_Player ID'].astype(str)
        
        # Lọc ra những ID chưa có trong file master
        new_records = processed_df[~processed_df['Club_Player ID'].isin(existing_master_df['Club_Player ID'])]
    else:
        existing_master_df = pd.DataFrame(columns=['Club_Player ID', 'Player ID', 'Club_ID'])
        new_records = processed_df

    # 5. XỬ LÝ LƯU DỮ LIỆU NẾU CÓ BẢN GHI MỚI
    if not new_records.empty:
        # A. Cập nhật file Master (Append)
        updated_master_df = pd.concat([existing_master_df, new_records], ignore_index=True)
        updated_master_df.to_excel(master_path, index=False)
        print(f"Đã cập nhật {len(new_records)} dòng mới vào file Master.")

        # B. Lưu file Import (Chỉ chứa dòng mới)
        new_records.to_excel(import_path, index=False)
        print(f"Đã lưu file import tại: {import_path}")

        # C. Ghi Log
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_ids_list = ", ".join(new_records['Club_Player ID'].tolist())
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"--- Cập nhật ngày: {now} ---\n")
            f.write(f"Số lượng ID mới: {len(new_records)}\n")
            f.write(f"Danh sách ID: {new_ids_list}\n")
            f.write("-" * 50 + "\n")
        
        print("Đã ghi log thành công.")
    else:
        print("Không có ID mới nào được tìm thấy. Không có gì để cập nhật.")

except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")
    import traceback
    traceback.print_exc()