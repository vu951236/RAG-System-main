import os
import time
import requests
import base64
from io import BytesIO
from PIL import Image

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Image as PDFImage
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


BASE_URL = "http://127.0.0.1:8000"
FONT_PATH = "C:/Windows/Fonts/Arial.ttf"

UPLOAD_TIMEOUT = 300
ASK_TIMEOUT = 60
RETRY_COUNT = 2

# CLEAN TEXT
import re

def clean_for_pdf(text):
    if not text:
        return ""
    
    # 1. Chuyển đổi các thực thể XML cơ bản trước
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    
    # 2. Khôi phục lại các thẻ định dạng mà ReportLab hỗ trợ
    # Chúng ta phải khôi phục sau khi đã escape < và > ở bước trên
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    text = text.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    text = text.replace("&lt;u&gt;", "<u>").replace("&lt;/u&gt;", "</u>")
    
    # 3. Xử lý thẻ <font color='red'>
    # Chuyển từ &lt;font color='red'&gt; sang đúng định dạng <font color="red">
    text = re.sub(r'&lt;font color=(?:\'|")(\w+)(?:\'|")&gt;', r'<font color="\1">', text)
    text = text.replace("&lt;/font&gt;", "</font>")

    # 4. QUAN TRỌNG: Sửa lỗi thẻ <br>
    # ReportLab yêu cầu <br/> (có dấu gạch chéo) chứ không phải <br>
    text = text.replace("&lt;br&gt;", "<br/>")
    text = text.replace("&lt;br/&gt;", "<br/>")
    text = text.replace("\n", "<br/>")

    # 5. Loại bỏ các ký tự điều khiển lỗi (như \uf06e hoặc các ký tự lạ gây crash parser)
    text = "".join(ch for ch in text if ord(ch) >= 32 or ch in "\n\r\t")
    
    return text

# EXPORT PDF
def export_to_pdf(data_results, filename="Ket_Qua_RAG_Highlight.pdf"):

    font_name = "Arial-Viet"

    try:
        pdfmetrics.registerFont(TTFont(font_name, FONT_PATH))
    except:
        font_name = "Helvetica"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    title_style = ParagraphStyle(
        'T',
        fontName=font_name,
        fontSize=18,
        alignment=1,
        spaceAfter=20
    )

    q_style = ParagraphStyle(
        'Q',
        fontName=font_name,
        fontSize=11,
        textColor=colors.dodgerblue,
        spaceAfter=6,
        leading=15
    )

    a_style = ParagraphStyle(
        'A',
        fontName=font_name,
        fontSize=10,
        leading=14,
        alignment=4
    )

    story = []

    story.append(Paragraph("<b>BÁO CÁO KẾT QUẢ TRUY VẤN RAG</b>", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.dodgerblue))
    story.append(Spacer(1, 20))

    for idx, item in enumerate(data_results):

        safe_q = clean_for_pdf(item["question"])
        safe_a = clean_for_pdf(item["answer"])

        story.append(
            Paragraph(f"<b>CÂU HỎI {idx+1}:</b> {safe_q}", q_style)
        )

        story.append(Paragraph(safe_a, a_style))

        # HÌNH ẢNH
        for res in item.get("raw_data", []):
            if res.get("image_data"):
                try:
                    img_bytes = base64.b64decode(res["image_data"])
                    img_buffer = BytesIO(img_bytes)
                    pil_img = Image.open(img_buffer)

                    if pil_img.mode != "RGB":
                        pil_img = pil_img.convert("RGB")

                    clean_buffer = BytesIO()
                    pil_img.save(clean_buffer, format="JPEG")
                    clean_buffer.seek(0)

                    pdf_img = PDFImage(clean_buffer, width=400, height=250)

                    story.append(Spacer(1, 10))
                    story.append(pdf_img)

                except:
                    continue

        meta = (
            f"<font size='8' color='#777777'>"
            f"Xử lý: {item['time']:.3f}s | "
            f"Nguồn: Trang {item['page']}"
            f"</font>"
        )

        story.append(Spacer(1, 6))
        story.append(Paragraph(meta, a_style))
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        story.append(Spacer(1, 15))

    doc.build(story)

    print("\nXuất PDF thành công:")
    print(os.path.abspath(filename))

# REQUEST CÓ RETRY
def safe_post(url, **kwargs):
    for attempt in range(RETRY_COUNT):
        try:
            return requests.post(url, **kwargs)
        except requests.exceptions.Timeout:
            print(f"Timeout lần {attempt+1} khi gọi {url}")
        except requests.exceptions.ConnectionError:
            print("Không kết nối được tới server RAG.")
            return None
    return None

# DEMO CHÍNH
def run_demo(target_pdf):
    # Khai báo ID giả định để backend phân loại collection
    USER_ID = "user_123"
    CONV_ID = "session_001"

    if not os.path.exists(target_pdf):
        print(f"Không tìm thấy file {target_pdf}")
        return

    print(f"Đang upload tài liệu: {target_pdf}...")

    try:
        with open(target_pdf, "rb") as f:
            # Thêm params vào URL để khớp với định nghĩa của FastAPI
            response = safe_post(
                f"{BASE_URL}/upload",
                params={"user_id": USER_ID, "conversation_id": CONV_ID},
                files={"file": f},
                timeout=UPLOAD_TIMEOUT
            )

            if not response or response.status_code != 200:
                detail = response.json() if response else "No response"
                print(f"Upload thất bại. Chi tiết: {detail}")
                return

    except Exception as e:
        print(f"Lỗi hệ thống khi upload: {e}")
        return

    print("Upload thành công.\n")

    test_questions = [
        "Bảo mật hệ thống thông tin được định nghĩa như thế nào?",
        "Ba yếu tố cốt lõi của mô hình CIA Triad là gì?",
        "Giải thích tính không thể chối bỏ và cho ví dụ trong ngân hàng.",
        "Sự khác biệt giữa Mối đe dọa và Lỗ hổng bảo mật là gì?",
        "Kể tên 7 vùng trong cơ sở hạ tầng CNTT.",
        "Luật Viễn thông 2023 có điểm gì đáng lưu ý?",
        "Quy trình bảo mật hệ thống thông tin gồm mấy bước?"
    ]

    all_results = []

    for q in test_questions:
        print(f"Đang hỏi: {q[:50]}...")
        start = time.time()

        # SỬA TẠI ĐÂY: Gửi kèm user_id và conversation_id trong body JSON
        payload = {
            "user_id": USER_ID,
            "conversation_id": CONV_ID,
            "question": q
        }

        response = safe_post(
            f"{BASE_URL}/ask",
            json=payload,
            timeout=ASK_TIMEOUT
        )

        if response and response.status_code == 200:
            data = response.json()
            
            # Lưu kết quả để xuất PDF
            all_results.append({
                "question": q,
                "answer": data.get("answer", "Không có câu trả lời"),
                "page": "Nhiều trang", # Bạn có thể lấy trang cụ thể từ raw_data nếu muốn
                "time": time.time() - start,
                "raw_data": data.get("raw_data", [])
            })
        else:
            status = response.status_code if response else "Timeout"
            print(f"Lỗi khi hỏi câu '{q[:20]}...': Status {status}")

    if all_results:
        export_to_pdf(all_results)
    else:
        print("Không có kết quả nào để xuất PDF.")

if __name__ == "__main__":
    run_demo("test.pdf")