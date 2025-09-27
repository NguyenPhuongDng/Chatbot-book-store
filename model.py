import re
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("GENAI_API_KEY")

genai.configure(api_key=api_key)
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

            Yêu cầu:
            - Chỉ sử dụng thông tin trong dữ liệu sách.
            - Nếu không có sách phù hợp, trả lời: "Xin lỗi, tôi không tìm thấy sách bạn cần."
            - Nếu có sách, hãy liệt kê đầy đủ theo định dạng:

            **Tên sách** – **Tác giả**  
            📚 Thể loại: xxx  
            💰 Giá: xxx VNĐ  
            📦 Số lượng: y cuốn  

            - Giữ văn phong ngắn gọn, thân thiện, lịch sự.
        """
    else:
        prompt = f"""
        Bạn là chatbot bán hàng của BookStore.  
        Nhiệm vụ: Trả lời ngắn gọn, thân thiện, lịch sự, tập trung vào sách và dịch vụ mua bán của cửa hàng.  

        Quy tắc:  
        1. Luôn trả lời theo ngữ cảnh "bán sách". Không tư vấn ngoài sách hoặc cửa hàng.  
        2. Nếu khách tìm sách → Hỏi chi tiết: tên sách, tác giả, thể loại.  
        3. Nếu khách muốn đặt hàng → Hỏi rõ tên sách để kiểm tra số lượng.  
        4. Nếu thông tin không thuộc phạm vi (sách/cửa hàng) → Trả lời: "Xin lỗi, tôi không biết về điều đó."  
        5. Không trả lời dài dòng. Tránh giải thích lý thuyết. Chỉ cung cấp thông tin cần thiết cho mua hàng.  
        Hãy trả lời câu hỏi sau của khách hàng.
        Câu hỏi: {message}
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


