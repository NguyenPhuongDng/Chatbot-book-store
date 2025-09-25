from flask import Flask, render_template, request, jsonify
import json, os
import model
import sqlite3

app = Flask(__name__)

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
    return rows

ORDERS_FILE = "orders.json"
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

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
        if isinstance(entities, dict):
            books = query_books_by_dict(entities)
            book_str = "\n".join([
                f"Tên sách: {title}, Tác giả: {author}, "
                f"Thể loại: {category}, Giá: {price}, Còn lại: {stock}"
                for _, title, author, price, stock, category in books
            ])
            response = model.generate_response_with_data(user_input, intent, book_str)
        else:
            response = entities

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
                response = "Xin lỗi! Quyển sách bạn muốn mua hiện đã hết hàng."
        else:
            response = "Bạn muốn đặt sách gì? Vui lòng cho tôi biết tên sách cụ thể."

    elif intent == "chat":
        response = model.generate_response_with_data(user_input, intent)

    return jsonify({"response": response})

@app.route("/order", methods=["POST"])
def order():
    data = request.json
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        orders = json.load(f)

    orders.append(data)

    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "success", "message": "Đơn hàng đã được lưu"})

@app.route("/orders", methods=["GET"])
def orders():
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        orders = json.load(f)
    return jsonify(orders)

if __name__ == "__main__":
    app.run(debug=True)