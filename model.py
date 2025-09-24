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


def extract_book_entities(message):
        """Trích xuất thông tin sách từ tin nhắn"""
        prompt = f"""
        Từ tin nhắn sau, hãy trích xuất thông tin về sách:
        - Tên sách
        - Tác giả  
        - Thể loại  
        Tin nhắn: "{message}"
        Trả về kết quả dưới dạng JSON nếu có ít nhất một trong ba thông tin:
        {{
            "title": "tên sách hoặc None",
            "author": "tác giả hoặc None", 
            "category": "thể loại hoặc None",
        }}
        Nếu không tìm thấy cả 3 thông tin trên Hãy trả về câu hỏi để hỏi khách hàng cung cấp thêm thông tin.
        """
        
        try:
            response = model.generate_content(prompt)
            # Parse JSON from response
            json_text = response.text.strip()
            # Remove markdown formatting if present
            json_text = re.sub(r'```json\n?', '', json_text)
            json_text = re.sub(r'\n?```', '', json_text)
            
            entities = json.loads(json_text)
            return entities
        except:
            return None

def generate_response_with_data(message, intent, book_data=None):
    """Tạo phản hồi từ AI với dữ liệu sách"""
    if intent == 'search' and book_data:
        prompt = f"""
        Khách hàng hỏi: "{message}"
        
        Dữ liệu sách từ cơ sở dữ liệu:
        {book_data}
        
        Hãy trả lời câu hỏi của khách hàng, chỉ sử dụng thông tin dữ liệu sách từ cơ sở dữ liệu.
        Nếu không có thông tin hãy nói không tìm thấy.
        Giữ câu trả lời ngắn gọn, thân thiện, lịch sự, đưa ra tất cả thông tin sách từ dữ liệu sách.
        """
    elif intent == 'order':
        prompt = f"""
        Khách hàng muốn đặt hàng: "{message}"
        
        Hãy phản hồi thân thiện và lịch sự.
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
