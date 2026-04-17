import json
import re
from pathlib import Path

# ===== CẤU HÌNH ĐƯỜNG DẪN =====
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

def clean_text(text):
    if not text: return ""
    # 1. Loại bỏ LaTeX
    text = re.sub(r'\$.*?\$', '', text)
    # 2. Thay thế dấu phân tách :::
    text = re.sub(r'\s*:::\s*', ' - ', text)
    # 3. Loại bỏ ký tự lạ (chỉ giữ lại chữ, số, dấu câu cơ bản)
    text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
    # 4. Loại bỏ khoảng trắng trước dấu câu
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    # 5. Chuẩn hóa dấu hai chấm lặp lại
    text = re.sub(r'[:]{2,}', ':', text)
    # 6. Chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_json_from_text(raw_content):
    """Trích xuất phần JSON nằm giữa các đoạn text rác"""
    start_idx = raw_content.find('{')
    end_idx = raw_content.rfind('}')
    if start_idx != -1 and end_idx != -1:
        return raw_content[start_idx:end_idx+1]
    return None

def process_and_save_exact_name(file_name):
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        print(f"❌ Không tìm thấy: {file_path}")
        return

    print(f"🔄 Đang xử lý: {file_name}...")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Tìm JSON trong file
    json_str = extract_json_from_text(content)
    all_text_segments = []

    if json_str:
        try:
            data = json.loads(json_str)
            
            # Trường hợp 1: Dictionary (Cấu trúc file3.txt)
            if isinstance(data, dict):
                if "section_name" in data:
                    all_text_segments.extend(data["section_name"])
                
                if "paragraphs" in data:
                    for section in data["paragraphs"]:
                        # Nếu paragraphs là list lồng list
                        if isinstance(section, list):
                            for para in section:
                                # Xóa tag - Đã sửa lỗi regex tại đây
                                clean_para = re.sub(r'\\', '', para)
                                all_text_segments.append(clean_para)
                        else:
                            clean_para = re.sub(r'\\', '', section)
                            all_text_segments.append(clean_para)
            
            # Trường hợp 2: List đơn giản (file1, file2)
            elif isinstance(data, list):
                all_text_segments.extend([str(item) for item in data])

        except Exception as e:
            print(f"⚠️ Lỗi parse JSON trong {file_name}: {e}")
            # Nếu lỗi parse, dùng toàn bộ nội dung file như text thuần
            all_text_segments = [content]
    else:
        # Nếu không có dấu hiệu JSON, dùng text thuần
        all_text_segments = [content]

    # Làm sạch từng đoạn và gộp lại
    cleaned_segments = [clean_text(seg) for seg in all_text_segments if seg]
    final_output = ". ".join(cleaned_segments)

    # Ghi đè vào file với tên gốc
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print(f"✅ Đã xử lý và ghi đè thành công: {file_name}")

if __name__ == "__main__":
    # Danh sách các file cần chạy
    target_files = ["file4.txt","file5.txt","file6.txt","file7.txt"]
    for filename in target_files:
        process_and_save_exact_name(filename)