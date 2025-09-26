from flask import Flask, render_template, request, jsonify
import json, os
import model
import sqlite3

app = Flask(__name__)

def init_orders_db():
    conn = sqlite3.connect("Orders.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            book_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

# Gọi hàm khởi tạo khi start app
init_orders_db()

def query_books_by_dict(filters: dict):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()

    conditions = []
    values = []

    for key, value in filters.items():
        if value is not None:
            conditions.append(f"{key} LIKE ?")
            values.append(f"%{value}%")

    sql = "SELECT * FROM books"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    cursor.execute(sql, values)
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries for easier access
    books_list = []
    for row in rows:
        book = {
            "book_id": row[0],
            "title": row[1], 
            "author": row[2],
            "price": row[3],
            "stock": row[4],
            "category": row[5]
        }
        books_list.append(book)
    
    return books_list

def get_all_orders():
    conn = sqlite3.connect("Orders.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.order_id, o.customer_name, o.phone, o.address, 
               o.book_id, b.title, b.author, b.price, o.quantity, o.status
        FROM Orders o
        LEFT JOIN books b ON o.book_id = b.book_id
        ORDER BY o.order_id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    orders_list = []
    for row in rows:
        order = {
            "order_id": row[0],
            "customer_name": row[1], 
            "phone": row[2],
            "address": row[3],
            "book_id": row[4],
            "book_title": row[5],
            "book_author": row[6], 
            "book_price": row[7],
            "quantity": row[8],
            "status": row[9]
        }
        orders_list.append(order)
    
    return orders_list

def update_order_status(order_id, status):
    conn = sqlite3.connect("Orders.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE Orders SET status = ? WHERE order_id = ?', (status, order_id))
    conn.commit()
    conn.close()

@app.route("/staff")
def home():
    return render_template("index.html")

@app.route("/")
def chat_page():
    return render_template("index_chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    user_form = data.get("form", None)
    
    intent = model.classify_intent(user_input)
    response = "Xin lỗi, hiện tôi chưa hiểu yêu cầu của bạn."

    if intent == "search":
        entities = model.extract_book_entities(user_input)
        if isinstance(entities, dict) and any(entities.values()):
            books = query_books_by_dict(entities)
            if len(books) == 0:
                response = f"Xin lỗi!\nChúng tôi không có quyển sách **{entities.get('title')}** trong kho."
            else:
                book_str = "\n".join([
                    f"Tên sách: {book['title']}, Tác giả: {book['author']}, "
                    f"Thể loại: {book['category']}, Giá: {book['price']}, Còn lại: {book['stock']}"
                    for book in books
                ])
                response = model.generate_response_with_data(user_input, intent, book_str)
        else:
            response = "Bạn muốn tìm sách nào?\nHãy cho tôi biết một trong ba thông tin sau:\n- **Tên sách**\n- **Tác giả**\n- **Thể loại**"

    elif intent == "order":
        entities = model.extract_book_entities(user_input)
        if isinstance(entities, dict) and entities.get("title") is not None:
            books = query_books_by_dict(entities)
            if books and books[0]["stock"] > 0:
                book = books[0]
                book_info = {
                    "book_id": book["book_id"],
                    "title": book["title"],
                    "author": book["author"],
                    "price": book["price"],
                    "stock": book["stock"]
                }
                response = {
                    "type": "form_request",
                    "book_found": True,
                    "book_info": book_info,
                    "form_fields": [
                        {"name": "customer_name", "label": "Họ tên", "type": "text", "value": ""},
                        {"name": "phone", "label": "Số điện thoại", "type": "text", "value": ""},
                        {"name": "address", "label": "Địa chỉ", "type": "text", "value": ""},
                        {"name": "book_id", "label": "Mã sách", "type": "hidden", "value": book_info["book_id"]},
                        {"name": "book_title", "label": "Tên sách", "type": "text", "value": book_info["title"], "readonly": True},
                        {"name": "quantity", "label": f"Số lượng (tối đa {book_info['stock']})", "type": "number", "value": "1", "max": book_info["stock"]}
                    ]
                }
            else:
                response = f"Rất tiếc!\nQuyển sách **{entities.get('title')}** đã hết hàng.\nBạn muốn tìm hoặc mua quyển sách khác không?"

        else:
            response = "Bạn muốn đặt quyển nào?\nHãy cho mình biết **tên sách** chính xác."


    elif intent == "chat":
        response = model.generate_response_with_data(user_input, intent)

    return jsonify({"response": response})

@app.route("/order", methods=["POST"])
def order():
    data = request.json
    
    # Lưu order vào SQLite database thay vì JSON file
    conn = sqlite3.connect("Orders.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO Orders (customer_name, phone, address, book_id, quantity, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('customer_name'),
        data.get('phone'), 
        data.get('address'),
        data.get('book_id'),
        data.get('quantity'),
        'pending'
    ))
    
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "success", "message": "Đơn hàng đã được lưu", "order_id": order_id})

@app.route("/orders", methods=["GET"])
def orders():
    orders = get_all_orders()
    return jsonify(orders)

@app.route("/orders/update", methods=["POST"])
def update_order():
    data = request.json
    order_id = data.get('order_id')
    status = data.get('status')
    
    if order_id and status:
        update_order_status(order_id, status)
        return jsonify({"status": "success", "message": "Cập nhật trạng thái đơn hàng thành công"})
    else:
        return jsonify({"status": "error", "message": "Thiếu thông tin order_id hoặc status"})

if __name__ == "__main__":
    app.run(debug=True)