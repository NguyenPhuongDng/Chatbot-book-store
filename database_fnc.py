# SQLite đơn giản
import sqlite3

DB_FILE = "books.db"

def connect():
    return sqlite3.connect(DB_FILE)

def search_books(query):
    conn = connect()
    c = conn.cursor()
    q = f"%{query}%"
    c.execute("""SELECT title, author, price, stock FROM Books
                 WHERE title LIKE ? OR author LIKE ? OR category LIKE ?""",
              (q, q, q))
    rows = c.fetchall()
    conn.close()
    return [{"title": r[0], "author": r[1], "price": r[2], "stock": r[3]} for r in rows]
