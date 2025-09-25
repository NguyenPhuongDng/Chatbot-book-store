import re
import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyB5zDpFEqzEQmBGK3axkLSqUKbNiUxzUWQ")
model = genai.GenerativeModel("gemini-2.5-flash-lite")

def classify_intent(message):
    prompt = f"""
        Ban là một trợ lý ảo cho cửa hàng sách trực tuyến.
        Phân loại tin nhắn sau thành một trong ba loại: "order", "search", hoặc "chat"
        
        - order: Khách hàng muốn đặt mua sách
        - search: Khách hàng muốn tìm kiếm thông tin sách
        - chat: Trò chuyện chung, hỏi đáp
        
        Tin nhắn: "{message}"
        
        Trả về chỉ một từ: order, search, hoặc chat
        """
    try:
        response = model.generate_content(prompt)
        intent = response.text.strip().lower()
        
        if intent in ['order', 'search', 'chat']:
            return intent
        else:
            return 'chat' 
    except:
        return 'chat'


import re, json

def extract_book_entities(message):
    """Trích xuất thông tin sách từ tin nhắn"""
    prompt = f"""
    Từ tin nhắn sau, hãy trích xuất thông tin về sách:
    - Tên sách/truyện
    - Tác giả  
    - Thể loại  
    Tin nhắn: "{message}"
    Trả về kết quả dưới dạng JSON:
    {{
        "title": "tên sách/truyện hoặc None",
        "author": "tác giả hoặc None", 
        "category": "thể loại hoặc None"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip()

        # loại bỏ ```json ... ```
        json_text = re.sub(r"```json\s*", "", json_text)
        json_text = re.sub(r"```", "", json_text)

        entities = json.loads(json_text)

        # đảm bảo có đủ key
        return {
            "title": entities.get("title"),
            "author": entities.get("author"),
            "category": entities.get("category")
        }
    except Exception as e:
        print("Extract error:", e)
        return {"title": None, "author": None, "category": None}


def generate_response_with_data(message, intent, book_data=None):
    """Tạo phản hồi từ AI với dữ liệu sách"""
    if intent == 'search' and book_data:
        prompt = f"""
        Khách hàng hỏi: "{message}"
        
        Dữ liệu sách từ cơ sở dữ liệu:
        {book_data}
        
        Hãy trả lời câu hỏi của khách hàng, chỉ sử dụng thông tin dữ liệu sách từ cơ sở dữ liệu.
        Nếu không có thông tin sách từ cơ sở dữ liệu hãy nói không tìm thấy.
        Giữ câu trả lời ngắn gọn, thân thiện, lịch sự, đưa ra tất cả thông tin sách từ dữ liệu sách.
        """
    elif intent == 'order':
        prompt = f"""
        Khách hàng muốn đặt hàng
        Hãy kiểm trả thông tin khách hàng xem đã nhập đúng định dạng thông tin của 3 trường nội dung
        Tên, Số điện thoại, Địa chỉ
        Dưới đây là thông tin khách hàng
        {book_data} 
        Nếu đúng định dạng thông tin, trả về "Correct", nếu không đúng trả về "Wrong"
        Trả về chỉ một từ: Correct hoặc Wrong
        """
    else:
        prompt = f"""
        Khách hàng nói: "{message}"
        
        Bạn là chatbot của BookStore - cửa hàng sách.
        Hãy trả lời thân thiện, hữu ích về chủ đề liên quan đến sách, đọc sách, hoặc dịch vụ của cửa hàng.
        Giữ câu trả lời ngắn gọn, thân thiện, lịch sự.
        Nếu không biết, hãy nói "Xin lỗi, tôi không biết về điều đó."
        Nếu khách hỏi tìm sách, hãy hỏi các thông tin cụ thể như tên sách, tác giả, thể loại.
        Nêu khách hỏi đặt hàng, Hãy hỏi cụ thể tên sách để tra cứu số lượng.
        """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        if intent == 'search':
            return "Xin lỗi, tôi không thể tìm kiếm sách lúc này. Vui lòng thử lại sau."
        elif intent == 'order':
            return "Bạn có thể sử dụng nút 'Đặt hàng' để tạo đơn hàng mới!"
        else:
            return "Xin lỗi, tôi không thể trả lời lúc này. Vui lòng thử lại sau."


