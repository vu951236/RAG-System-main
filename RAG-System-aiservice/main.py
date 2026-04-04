from fastapi import FastAPI, UploadFile, File
import uvicorn
import pypdf
import uuid
import os
import base64
import easyocr
import numpy as np
import cv2
import re
from algorithms import manual_chunking

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

from algorithms import (
    tokenize,
    compute_tf,
    compute_idf,
    calculate_cosine_similarity
)

app = FastAPI(title="Production RAG with Qdrant")

reader = easyocr.Reader(['vi', 'en'])
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
client = QdrantClient(url=qdrant_url)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===== UTILS =====

def is_meaningful_chunk(chunk, min_words=15):
    text = chunk["text"].strip()

    if chunk.get("image_data"):
        return True

    words = re.findall(r'\w+', text)

    if len(words) < min_words:
        return False

    if text.isupper():
        return False

    return True

def ask_question_logic(query, chunks, idf_dict):
    query_tokens = tokenize(query)
    
    query_bigrams = [f"{query_tokens[i].lower()} {query_tokens[i+1].lower()}" 
                     for i in range(len(query_tokens) - 1)]

    if not query_bigrams:
        return {"status": "No Result", "answer": "Vui lòng nhập câu hỏi dài hơn 2 từ.", "raw_data": []}

    query_tf = compute_tf(query_tokens)
    results = []
    seen_texts = set()

    for chunk in chunks:

        if not chunk_contains_exact_bigram(chunk["text"], query_tokens):
            continue

        if not is_meaningful_chunk(chunk):
            continue

        score = calculate_cosine_similarity(query_tf, chunk["tf"], idf_dict)

        if score > 0.05:

            highlighted_text = highlight_exact_bigrams(chunk["text"], query_tokens)

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

    text_results = [r for r in results if not r.get("image_data")]
    image_results = [r for r in results if r.get("image_data")]

    top_results = text_results[:15]

    matched_pages = {r["page"] for r in top_results}

    for img in image_results:
        if img["page"] in matched_pages:
            top_results.append(img)

    if not any(r.get("image_data") for r in top_results):
        top_results.extend(image_results[:3])

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

def ensure_collection(collection_name):
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)
    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384, 
                distance=models.Distance.COSINE
            ),
        )

def minimal_normalize(text):
    return " ".join(text.split()) if text else ""

def chunk_contains_exact_bigram(text, query_tokens):
    if len(query_tokens) < 2: return False
    text_lower = text.lower()
    for i in range(len(query_tokens) - 1):
        bigram = query_tokens[i].lower() + " " + query_tokens[i+1].lower()
        if re.search(r'\b' + re.escape(bigram) + r'\b', text_lower):
            return True
    return False

def highlight_exact_bigrams(text, query_tokens):
    if len(query_tokens) < 2: return text
    for i in range(len(query_tokens) - 1):
        bigram = query_tokens[i].lower() + " " + query_tokens[i+1].lower()
        text = re.sub(
            r'\b' + re.escape(bigram) + r'\b',
            lambda m: f"<font color='red'><b>{m.group()}</b></font>",
            text, flags=re.IGNORECASE
        )
    return text

# ===== UPLOAD =====

@app.post("/upload")
async def upload_document(user_id: str, conversation_id: str, file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    pdf = pypdf.PdfReader(file_path)
    collection_name = f"user_{user_id}_conv_{conversation_id}"
    ensure_collection(collection_name)

    points = []

    for page_idx, page in enumerate(pdf.pages):
        page_number = page_idx + 1
        text = minimal_normalize(page.extract_text() or "")

        # ✅ FIX: dùng manual_chunking
        if text:
            page_chunks = manual_chunking(text, page_number=page_number)

            for chunk_data in page_chunks:
                tokens = tokenize(chunk_data["text"])

                if tokens:
                    points.append(models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=model.encode(chunk_data["text"]).tolist(),
                        payload={
                            "text": chunk_data["text"],
                            "page": page_number,
                            "image": None 
                        }
                    ))

        # OCR
        try:
            for img_file in page.images:
                img_bytes = img_file.data
                nparr = np.frombuffer(img_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None: continue

                ocr_result = reader.readtext(image, detail=0)
                text_img = minimal_normalize(" ".join(ocr_result))

                if len(text_img.strip()) > 3:
                    encoded_img = base64.b64encode(img_bytes).decode()

                    points.append(models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=model.encode(text_img).tolist(),
                        payload={
                            "text": f"[Nội dung ảnh]: {text_img}",
                            "page": page_number,
                            "image": encoded_img
                        }
                    ))
        except Exception as e:
            print(f"OCR error on page {page_number}: {e}")

    if points:
        client.upsert(collection_name=collection_name, points=points)

    return {"status": "Success", "total_chunks": len(points)}

# ===== ASK =====

@app.post("/ask")
async def ask_ai(data: dict):

    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")
    question = data.get("question")

    if not all([user_id, conversation_id, question]):
        return {"status": "Error", "answer": "Thiếu dữ liệu"}

    collection_name = f"user_{user_id}_conv_{conversation_id}"

    # ✅ FIX: lấy toàn bộ data thay vì vector search
    all_points, _ = client.scroll(
        collection_name=collection_name,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )

    if not all_points:
        return {
            "status": "No Result",
            "answer": "Không có dữ liệu.",
            "raw_data": []
        }

    chunks = []

    for point in all_points:
        text = point.payload.get("text", "")
        tokens = tokenize(text)

        if not tokens:
            continue

        chunks.append({
            "text": text,
            "page": point.payload.get("page", "?"),
            "tokens": tokens,
            "tf": compute_tf(tokens),
            "image_data": point.payload.get("image")
        })

    if not chunks:
        return {
            "status": "No Result",
            "answer": "Dữ liệu không xử lý được.",
            "raw_data": []
        }

    idf_dict = compute_idf([c["tokens"] for c in chunks])

    result = ask_question_logic(question, chunks, idf_dict)
    result["total_chunks"] = len(chunks)

    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)