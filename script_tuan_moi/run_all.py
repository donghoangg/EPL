import subprocess
import os
import sys

# Danh sách 14 file theo đúng thứ tự bạn cung cấp
scripts = [
    r"E:\project 1\script_tuan_moi\player_info.py",
    r"E:\project 1\script_tuan_moi\cao_link.py",
    r"E:\project 1\script_tuan_moi\cao_link_gk.py",
    r"E:\project 1\script_tuan_moi\cao_player_matchlog.py",
    r"E:\project 1\script_tuan_moi\cao_goalkeeper_matchlog.py",
    r"E:\project 1\script_tuan_moi\Club_player.py",
    r"E:\project 1\script_tuan_moi\match.py",
    r"E:\project 1\script_tuan_moi\Club_player_matchlog.py",
    r"E:\project 1\script_tuan_moi\xuly_match_log.py",
    r"E:\project 1\script_tuan_moi\import_player.py",
    r"E:\project 1\script_tuan_moi\import_Club_player.py",
    r"E:\project 1\script_tuan_moi\import_match.py",
    r"E:\project 1\script_tuan_moi\import_club_player_matchlog.py",
    r"E:\project 1\script_tuan_moi\import_performance.py"
]

def run_scripts():
    for path in scripts:
        # Lấy tên file để hiển thị cho đẹp
        script_name = os.path.basename(path)
        # Lấy thư mục chứa file để chạy script tại đúng vị trí đó
        script_dir = os.path.dirname(path)
        
        print(f"\n{'='*50}")
        print(f"ĐANG CHẠY: {script_name}")
        print(f"{'='*50}")
        
        try:
            # Chạy file python. 
            # shell=True giúp xử lý tốt hơn trên Windows với đường dẫn có dấu cách
            result = subprocess.run(
                [sys.executable, path], 
                cwd=script_dir,      # Thiết lập môi trường chạy tại thư mục của file đó
                check=True           # Nếu file này lỗi (crash), nó sẽ dừng lại không chạy file sau
            )
            print(f" HOÀN THÀNH: {script_name}")
            
        except subprocess.CalledProcessError as e:
            print(f" LỖI: File {script_name} gặp sự cố. Dừng tiến trình.")
            break # Dừng lại nếu có 1 file bị lỗi để bạn kiểm tra
        except Exception as e:
            print(f" LỖI KHÔNG XÁC ĐỊNH: {e}")
            break

    print(f"\n{'='*50}")
    print("TẤT CẢ CÁC FILE ĐÃ ĐƯỢC XỬ LÝ XONG!")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_scripts()