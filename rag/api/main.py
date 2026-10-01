
import re
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from pypdf import PdfReader

app = FastAPI(title="CampusSaathi AI - RAG API", version="1.0.0")

chunks_store = []
metadata_store = []
pages_store = []

STOP_WORDS = {
    "what", "where", "when", "which", "who", "how", "is", "are",
    "the", "a", "an", "of", "in", "for", "to", "with", "does",
    "do", "and", "at", "on", "tell", "me", "about", "please",
    "can", "you", "provide", "available", "information", "give",
    "explain", "much", "many", "does", "college", "engineering"
}

NOT_FOUND = (
    "This information was not found in the available "
    "ABES FAQ document. Please check the official college website."
)

BASE_DIR = Path(__file__).resolve().parents[2]

POSSIBLE_PDF_PATHS = [
    BASE_DIR / "rag" / "data" / "ABES_FAQ.pdf",
    BASE_DIR / "data" / "ABES_FAQ.pdf",
    Path("rag/data/ABES_FAQ.pdf"),
    Path("../data/ABES_FAQ.pdf"),
    Path("data/ABES_FAQ.pdf"),
    Path(
        "C:/Users/Nitish Kasana/Desktop/"
        "CampusSaathi-AI/rag/data/ABES_FAQ.pdf"
    ),
]


def get_words(text: str) -> set:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 2 and word not in STOP_WORDS
    }


def load_pdf_file(filepath: Path) -> bool:
    global chunks_store, metadata_store, pages_store

    if not filepath.exists():
        print(f"[RAG] PDF not found: {filepath}")
        return False

    try:
        reader = PdfReader(str(filepath))
        new_chunks = []
        new_metadata = []
        new_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()

            if not text:
                print(f"[RAG] Page {page_number}: no extractable text")
                continue

            new_pages.append({
                "source": filepath.name,
                "page": page_number,
                "text": text,
            })

            # Keep overlapping chunks for retrieval.
            chunk_size = 700
            overlap = 120
            step = chunk_size - overlap

            for start in range(0, len(text), step):
                chunk = text[start:start + chunk_size]

                if len(chunk.strip()) > 20:
                    new_chunks.append(chunk)
                    new_metadata.append({
                        "source": filepath.name,
                        "page": page_number,
                    })

        chunks_store = new_chunks
        metadata_store = new_metadata
        pages_store = new_pages

        print(f"[RAG] PDF: {filepath.name}")
        print(f"[RAG] PDF pages: {len(reader.pages)}")
        print(f"[RAG] Pages with extractable text: {len(pages_store)}")
        print(f"[RAG] Extracted {len(chunks_store)} chunks")

        return bool(pages_store)

    except Exception as exc:
        print(f"[RAG] PDF loading failed: {exc}")
        return False


def auto_ingest_default_pdf():
    for path in POSSIBLE_PDF_PATHS:
        if path.exists() and load_pdf_file(path):
            return True

    print("[RAG] Could not find ABES_FAQ.pdf")
    return False


@app.on_event("startup")
def startup_event():
    auto_ingest_default_pdf()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: str


@app.get("/health")
def health_check():
    if not pages_store:
        auto_ingest_default_pdf()

    return {
        "status": "ok",
        "service": "CampusSaathi AI RAG Service",
        "pdf_pages_loaded": len(pages_store),
        "indexed_chunks": len(chunks_store),
        "gemini_configured": False,
        "search_mode": "local PDF text search",
    }


@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    temp_path = Path(__file__).resolve().parent / "uploaded_temp.pdf"

    try:
        content = await file.read()
        temp_path.write_bytes(content)

        if not load_pdf_file(temp_path):
            raise HTTPException(
                status_code=500,
                detail="The PDF could not be read or contains no extractable text."
            )

        # Preserve the uploaded filename in source metadata.
        for item in pages_store:
            item["source"] = file.filename

        for item in metadata_store:
            item["source"] = file.filename

        return {
            "message": f"Successfully ingested {file.filename}",
            "pages_loaded": len(pages_store),
            "total_chunks": len(chunks_store),
        }

    finally:
        if temp_path.exists():
            temp_path.unlink()


def extract_concise_answer(question: str, context: str) -> str:
    query_words = get_words(question)

    if not query_words:
        return NOT_FOUND

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in context.splitlines()
        if line.strip()
    ]

    # Parse numbered FAQ questions and their answers.
    qa_pairs = []
    current_question = ""
    current_answer = []

    question_pattern = re.compile(
        r"^\s*Q\s*\d+\s*[.):\-]\s*(.*)$",
        re.IGNORECASE,
    )
    answer_pattern = re.compile(
        r"^\s*(?:A|Ans|Answer)\s*:\s*(.*)$",
        re.IGNORECASE,
    )

    for line in lines:
        # A PDF header is not an answer.
        if any(header in line.lower() for header in (
            "knowledge-base draft",
            "campussaathi ai",
            "uniassist ai",
        )):
            continue

        q_match = question_pattern.match(line)

        if q_match:
            if current_question and current_answer:
                qa_pairs.append(
                    (current_question, " ".join(current_answer).strip())
                )

            current_question = q_match.group(1).strip()
            current_answer = []

            # Handle Q and A written on the same line.
            inline = re.search(
                r"\b(?:A|Ans|Answer)\s*:\s*(.*)$",
                current_question,
                re.IGNORECASE,
            )

            if inline:
                current_answer.append(inline.group(1).strip())
                current_question = current_question[:inline.start()].strip()

        else:
            a_match = answer_pattern.match(line)

            if a_match and current_question:
                current_answer.append(a_match.group(1).strip())
            elif current_answer and current_question:
                current_answer.append(line)
            elif current_question:
                current_question += " " + line

    if current_question and current_answer:
        qa_pairs.append(
            (current_question, " ".join(current_answer).strip())
        )

    # Match the user's question to FAQ question text.
    best_answer = ""
    best_score = 0.0

    for faq_question, faq_answer in qa_pairs:
        faq_words = get_words(faq_question)
        overlap = query_words & faq_words

        if not overlap or not faq_answer.strip():
            continue

        score = len(overlap) / len(query_words)

        if score > best_score:
            best_score = score
            best_answer = faq_answer

    if best_answer and best_score >= 0.30:
        return best_answer.strip()

    # If no explicit Q&A matches, only use relevant lines.
    # Never return an arbitrary first answer.
    candidates = []

    for i, line in enumerate(lines):
        lower = line.lower()

        if lower.startswith(("q", "a:", "ans:", "answer:")):
            continue

        line_words = get_words(line)
        overlap = query_words & line_words

        if not overlap:
            continue

        score = len(overlap) / len(query_words)

        if score >= 0.40:
            candidates.append((score, i, line))

    candidates.sort(key=lambda item: item[0], reverse=True)

    if not candidates:
        return NOT_FOUND

    best_score = candidates[0][0]

    # If multiple equally relevant lines exist, keep the answer concise.
    selected = []
    for score, _, line in candidates:
        if score < max(0.40, best_score - 0.15):
            continue

        if line not in selected:
            selected.append(line)

        if len(selected) >= 2:
            break

    if not selected:
        return NOT_FOUND

    return " ".join(selected)


def score_page(question: str, page_text: str) -> float:
    query_words = get_words(question)
    page_words = get_words(page_text)

    if not query_words or not page_words:
        return 0.0

    overlap = query_words & page_words
    return len(overlap) / len(query_words)


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if not pages_store:
        auto_ingest_default_pdf()

    if not pages_store:
        return ChatResponse(
            answer="The ABES FAQ PDF could not be loaded. Please check rag/data/ABES_FAQ.pdf.",
            sources=[],
            confidence="low",
        )

    # Search complete pages so answers are not lost at chunk boundaries.
    scored_pages = []

    for page in pages_store:
        score = score_page(question, page["text"])

        if score > 0:
            scored_pages.append((score, page))

    scored_pages.sort(key=lambda item: item[0], reverse=True)

    if not scored_pages:
        return ChatResponse(
            answer=NOT_FOUND,
            sources=[],
            confidence="low",
        )

    # Try the most relevant page first.
    best_score, best_page = scored_pages[0]
    answer = extract_concise_answer(question, best_page["text"])

    if answer == NOT_FOUND:
        return ChatResponse(
            answer=NOT_FOUND,
            sources=[],
            confidence="low",
        )

    source = f"{best_page['source']} (Page {best_page['page']})"

    return ChatResponse(
        answer=answer,
        sources=[source],
        confidence="medium",
    )