from fastapi import FastAPI, UploadFile, File
import uvicorn
import pypdf
import os
import re
import easyocr
import base64

from algorithms import (
    tokenize,
    manual_chunking,
    compute_tf,
    compute_idf,
    calculate_cosine_similarity
)

app = FastAPI(title="Universal Precision Search RAG with OCR + Highlight")

reader = easyocr.Reader(['vi', 'en'])

knowledge_base = []
idf_brain = {}

# TEXT NORMALIZE
def minimal_normalize(text):
    if not text:
        return ""
    return " ".join(text.split())

# HIGHLIGHT (CHỮ ĐỎ)
def highlight_text(content_text, query_tokens):

    highlighted = content_text

    words = sorted(
        list(set([w for w in query_tokens if len(w) > 1])),
        key=len,
        reverse=True
    )

    for word in words:
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f'<font color="#ff0000"><b>{m.group(0)}</b></font>',
            highlighted
        )

    return highlighted

# ASK LOGIC
def ask_question_logic(query, chunks, idf_dict):

    query_tokens = tokenize(query)

    if not query_tokens:
        return {
            "status": "No Query",
            "answer": "Không tìm thấy từ khóa đủ mạnh.",
            "page": 0,
            "raw_data": []
        }

    query_tf = compute_tf(query_tokens)
    results = []
    seen_texts = set()

    for chunk in chunks:

        score = calculate_cosine_similarity(query_tf, chunk["tf"], idf_dict)

        if score > 0.05:

            highlighted_text = highlight_text(chunk["text"], query_tokens)

            snippet = chunk["text"][:100]

            if snippet not in seen_texts:
                results.append({
                    "text": highlighted_text,
                    "page": chunk["page"],
                    "score": round(score, 3),
                    "image_data": chunk.get("image_data")
                })
                seen_texts.add(snippet)

    results.sort(key=lambda x: x["score"], reverse=True)

    if not results:
        return {
            "status": "No Result",
            "answer": "Không tìm thấy nội dung phù hợp.",
            "page": 0,
            "raw_data": []
        }

    # Phân loại text và ảnh
    text_results = [r for r in results if not r.get("image_data")]
    image_results = [r for r in results if r.get("image_data")]

    top_results = text_results[:15]

    matched_pages = {r["page"] for r in top_results}

    for img in image_results:
        if img["page"] in matched_pages:
            top_results.append(img)

    if not any(r.get("image_data") for r in top_results):
        top_results.extend(image_results[:3])

    # Build HTML
    full_body = ""

    for r in top_results:
        source_label = " [DỮ LIỆU TỪ ẢNH]" if r.get("image_data") else ""
        full_body += (
            f"<b>Trang {r['page']}{source_label} "
            f"(Score: {r['score']}):</b><br/>"
            f"{r['text']}<br/><br/>---<br/><br/>"
        )

    return {
        "status": "Success",
        "answer": full_body,
        "page": top_results[0]["page"],
        "raw_data": top_results
    }


# UPLOAD PDF
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        knowledge_base.clear()
        pdf = pypdf.PdfReader(temp_path)

        for page_idx, page in enumerate(pdf.pages):
            page_number = page_idx + 1

            # -------- TEXT --------
            raw_content = page.extract_text() or ""
            content = minimal_normalize(raw_content)

            if content.strip():
                page_chunks = manual_chunking(content, page_number=page_number)

                for chunk_data in page_chunks:
                    tokens = tokenize(chunk_data["text"])

                    if tokens:
                        knowledge_base.append({
                            "text": chunk_data["text"],
                            "page": page_number,
                            "tokens": tokens,
                            "tf": compute_tf(tokens)
                        })

            # -------- IMAGE OCR --------
            try:
                for img_obj in page.images:
                    img_bytes = img_obj.data

                    ocr_results = reader.readtext(img_bytes, detail=0)
                    ocr_text = minimal_normalize(" ".join(ocr_results))

                    if len(ocr_text.strip()) > 3:

                        encoded_img = base64.b64encode(img_bytes).decode("utf-8")
                        tokens = tokenize(ocr_text)

                        knowledge_base.append({
                            "text": f"[Nội dung ảnh]: {ocr_text}",
                            "page": page_number,
                            "tokens": tokens,
                            "tf": compute_tf(tokens),
                            "image_data": encoded_img
                        })

            except Exception:
                continue

        global idf_brain
        idf_brain = compute_idf([item["tokens"] for item in knowledge_base])

        return {
            "status": "Success",
            "total_chunks": len(knowledge_base)
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ASK API
@app.post("/ask")
async def ask_ai(data: dict):

    question = data.get("question", "")

    if not knowledge_base:
        return {
            "status": "No Data",
            "answer": "Vui lòng upload tài liệu trước.",
            "raw_data": []
        }

    return ask_question_logic(question, knowledge_base, idf_brain)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
