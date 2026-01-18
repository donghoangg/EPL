# Hệ thống thu thập, xử lý và trực quan hóa dữ liệu hiệu suất cầu thủ bóng đá

## 1. Mô tả dự án

Đây là dự án xây dựng một hệ thống dữ liệu hoàn chỉnh với mục tiêu tự động thu thập dữ liệu sản phẩm từ trang web FBRef. Sau khi thu thập, dữ liệu sẽ được xử lý, làm sạch và cuối cùng được trực quan hóa trên Power BI Dashboard để phục vụ cho việc phân tích.
## 2. Sơ lược về hệ thống

Hệ thống được thiết kế để hoạt động một cách tự động theo lịch trình định sẵn:

1.  **Lập lịch (Scheduler)**: Đóng vai trò là trình điều phối trung tâm, sử dụng Window Scheduler để tiến hành lập lịch và vào dữ liệu hàng tuần sau khi mỗi vòng đấu kết thúc
2.  ** Thu thập dữ liệu và xử lý**: Các đoạn mã nguồn trong thư mục 'Script_tuan_moi" có trách nhiệm thu thập dữ liệu từ web, tiến hành chỉnh sửa dữ liệu sau đó nạp vào database và data warehouse
3.  **Trực quan hóa (Visualization)**:
    *   File `Dashboard.pbix` là một Power BI Dashboard đã được thiết kế sẵn.
    *   Người dùng có thể mở file này bằng Power BI Desktop để xem các biểu đồ và phân tích đã được xây dựng từ dữ liệu đã qua xử lý.

## 3. Cấu trúc thư mục

```
.
├── ETL data 2018_2025/        # Thư mục chứa các Script thực hiện cào và xử lý các dữ liệu trong quá khứ
├── data clean/                # Thư mục chứa dữ liệu đã được xử lý để import và cơ sở dữ liệu 
├── data_import/               # Thư mục chứa dữ liệu để thực hiện import dữ liệu mới hàng tuần
├── log/                  
│   └──scraping                # Chứa các file nhật ký về quá trình cào dữ liệu
│   └──ETL                     # Chưa các file nhật ký về quá trình xử lý dữ liệu
│   └──import                  # Chứa các file nhật ký về quá trình import dữ liệu
├── Script_tuan_moi/
│   └── link_matchlog          # Chứa các đường dẫn của các trang cần cào dữ liệu
│   └──matchlog                # Dữ liệu được cào về hàng tuần chưa xử lý
│   └──script                  # Chứa các đoạn mã để xử lý quy trình hàng tuần
│   └──run_all.py              # Đoạn code điều phối quy trình làm việc
├── EDA.ipyng                  # Script chính để thực hiện khai phá dữ liệu
├── Dashboard.pbix             # File Power BI Dashboard
├── database.sql               # Thực hiện xây cơ sở dữ liệu theo mô hình OLTP
├── datawarehouse.sql          # Thực hiện xây kho dữ liệu theo mô hình OLAP
├── dashboard.pbix             # File Power BI Dashboard
└── report.pdf                 # Báo cáo của dự án
```
## 4. Kiến trúc hệ thống

<img width="4052" height="2554" alt="pipeline" src="https://github.com/user-attachments/assets/d95ab750-c90b-44d9-9785-bcd5f7b346e0" />

## 5. Dashboard
<img width="1091" height="714" alt="dash1" src="https://github.com/user-attachments/assets/82c589ef-eca0-441c-b01a-98e1e125bc06" />
<img width="1089" height="760" alt="dash2" src="https://github.com/user-attachments/assets/68b3dee7-4873-4597-b68d-ac5d4335e113" />

