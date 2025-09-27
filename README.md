# Chatbot Book Store

Ứng dụng web quản lý đơn hàng cho cửa hàng sách, được xây dựng bằng **Flask**, **SQLite** và tích hợp **Gemini API** để hỗ trợ chatbot.

---

## 1. Yêu cầu môi trường

* Python 3
* pip (trình quản lý gói Python)
* Tài khoản Google AI Studio để lấy **Gemini API Key**

---

## 2. Cài đặt

### Clone dự án

```bash
git clone https://github.com/NguyenPhuongDng Chatbot-book-store.git
```

### Cài các gói cần thiết

```bash
pip install -r requirements.txt
```

---

## 3. Cấu hình API Key
### Sử dụng file `.env`

Tạo file `.env` trong thư mục gốc dự án(Nếu chưa có):

```
GENAI_API_KEY=your_api_key
```
---

## 5. Chạy ứng dụng

```bash
python app.py
```

Giao diện chat bot của hệ thống sẽ chạy tại:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

Xem thông tin đơn hàng và quản lý đơn hàng tại:
[http://127.0.0.1:5000/staff](http://127.0.0.1:5000/staff)

---

## 6. Các chức năng chính

* **Quản lý đơn hàng:** tạo mới, xem danh sách, cập nhật trạng thái.
* **Chatbot hỗ trợ:** hỏi/đáp/tìm kiếm/tạo đơn hàng tự động với AI (Gemini API).
* **Lưu dữ liệu:** toàn bộ thông tin được lưu trong SQLite file `Orders.db` và `books.db`.

---

