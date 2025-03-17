# Blockchain Digital Asset Management System

Hệ thống quản lý quyền sở hữu tài sản số sử dụng Blockchain với lưu trữ SQLite.

## Cấu trúc thư mục

```
blockchain-asset-management/
├── before-optimization/     # Phiên bản trước cải tiến
│   ├── server.py           # Máy chủ với tra cứu tuần tự
│   ├── client.py           # Giao diện người dùng
│   └──       # Database SQLite
│
├── after-optimization/     # Phiên bản sau cải tiến
│   ├── server.py          # Máy chủ với tra cứu tối ưu
│   ├── client.py          # Giao diện người dùng
│   └──     # Database SQLite
|
|── blockchain.db           # Database SQLite chung
└── README.md


## Phiên bản trước cải tiến (before-optimization)

### Đặc điểm
- Tra cứu tuần tự qua blockchain
- Thời gian phản hồi: ~1-2 giây
- Lưu trữ dữ liệu bền vững với SQLite

### Cách chạy
1. Khởi động máy chủ:
```bash
cd before-optimization
python server.py
```

2. Khởi động máy khách:
```bash
python client.py
```

## Phiên bản sau cải tiến (after-optimization)

### Đặc điểm
- Sử dụng bảng băm để tra cứu nhanh
- Thời gian phản hồi: ~0.01 giây
- Hỗ trợ xử lý đa luồng
- Lưu trữ dữ liệu bền vững với SQLite

### Cách chạy
1. Khởi động máy chủ:
```bash
cd after-optimization
python server.py
```

2. Khởi động máy khách:
```bash
python client.py
```

## Yêu cầu hệ thống
- Python 3.7+
- SQLite3
- Thư viện tkinter cho giao diện người dùng

## Cài đặt thư viện
```bash
pip install sqlite3
```

## Chức năng chính
1. Đăng ký tài sản số mới
2. Xác thực quyền sở hữu tài sản
3. Lưu trữ dữ liệu blockchain bền vững

## So sánh hiệu suất

| Tiêu chí | Trước cải tiến | Sau cải tiến |
|----------|----------------|--------------|
| Cấu trúc dữ liệu | Blockchain (danh sách) | Blockchain + Bảng băm |
| Độ phức tạp tra cứu | O(n) | O(1) |
| Thời gian phản hồi | ~1-2 giây | ~0.01 giây |
| Xử lý | Đơn luồng | Đa luồng |

## Cấu trúc Database

### Bảng `blocks`
- `asset_id` (TEXT): Mã tài sản
- `asset_name` (TEXT): Tên tài sản
- `owner` (TEXT): Chủ sở hữu
- `prev_hash` (TEXT): Hash của block trước

## Đóng góp
Mọi đóng góp đều được hoan nghênh. Vui lòng tạo pull request hoặc báo cáo issues.

## Giấy phép
[MIT License](LICENSE)