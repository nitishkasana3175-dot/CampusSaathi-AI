import sys
from pathlib import Path
from pypdf import PdfReader

pdf_path = Path("C:/Users/Nitish Kasana/Desktop/CampusSaathi-AI/rag/data/ABES_FAQ.pdf")

if not pdf_path.exists():
    print(f"FAILED: PDF not found at {pdf_path}")
    sys.exit(1)

reader = PdfReader(str(pdf_path))
print(f"SUCCESS: Successfully opened {pdf_path.name}")
print(f"Total Pages: {len(reader.pages)}")

text_sample = reader.pages[0].extract_text()
print(f"Page 1 Sample Text:\n{text_sample[:300]}")
