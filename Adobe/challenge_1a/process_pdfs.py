import os
import json
import re
import fitz  # PyMuPDF
from utils import classify_headings

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def clean_text(text):
    """Remove newlines and extra spaces from text."""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    title = doc.metadata.get("title") or os.path.basename(pdf_path).replace(".pdf", "")
    outline = []

    for page_number, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")
        for b in blocks:
            text = clean_text(b[4])
            if text:
                level = classify_headings(text)
                if level:
                    outline.append({
                        "level": level,
                        "text": text,
                        "page": page_number
                    })
    return {"title": title, "outline": outline}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith(".pdf"):
            output = process_pdf(os.path.join(INPUT_DIR, file))
            out_path = os.path.join(OUTPUT_DIR, file.replace(".pdf", ".json"))
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
