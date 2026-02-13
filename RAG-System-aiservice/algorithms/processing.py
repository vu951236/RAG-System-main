import re

STOPWORDS = set([
    "là", "của", "và", "các", "có", "trong", "được", "những", "cho", "với", 
    "một", "về", "đến", "như", "thế", "nào", "gì", "đâu", "này", "kia", 
    "mấy", "bao", "nhiêu", "tại", "theo", "vậy", "nhé", "nha", "đó",
    "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười"
])

def tokenize(text):
    """Giữ lại từ >= 2 ký tự để không mất các thực thể như '7' vùng, 'NĐ' 13, 'CIA'."""
    words = re.findall(r'\w+', text.lower())
    # Chỉnh len(w) >= 2 để lấy được các từ khóa
    tokens = [w for w in words if w not in STOPWORDS and len(w) >= 2]
    return tokens

def manual_chunking(text, page_number, size=400, overlap=80):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= size:
            current_chunk += (" " + sentence if current_chunk else sentence)
        else:
            if current_chunk:
                chunks.append({"text": current_chunk.strip(), "page": page_number})
            
            # Giữ lại một phần overlap để không mất ngữ cảnh giữa các đoạn
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text.strip() + " " + sentence

    if current_chunk:
        chunks.append({"text": current_chunk.strip(), "page": page_number})
    return chunks