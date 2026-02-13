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
def clean_for_pdf(text):
    if not text:
        return ""
    text = text.replace("&", "&amp;")
    text = text.replace("\n", "<br/>")
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

    if not os.path.exists(target_pdf):
        print(f"Không tìm thấy file {target_pdf}")
        return

    print("Upload tài liệu...")

    try:
        with open(target_pdf, "rb") as f:
            response = safe_post(
                f"{BASE_URL}/upload",
                files={"file": f},
                timeout=UPLOAD_TIMEOUT
            )

            if not response or response.status_code != 200:
                print("Upload thất bại.")
                return

    except Exception as e:
        print(f"Lỗi upload: {e}")
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

        response = safe_post(
            f"{BASE_URL}/ask",
            json={"question": q},
            timeout=ASK_TIMEOUT
        )

        if response and response.status_code == 200:
            data = response.json()

            all_results.append({
                "question": q,
                "answer": data.get("answer", ""),
                "page": data.get("page", "N/A"),
                "time": time.time() - start,
                "raw_data": data.get("raw_data", [])
            })
        else:
            print("Không nhận được phản hồi.")

    if all_results:
        export_to_pdf(all_results)


if __name__ == "__main__":
    run_demo("test.pdf")
