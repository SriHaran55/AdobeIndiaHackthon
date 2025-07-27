
import os
import json
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import fitz  # PyMuPDF

def extract_sections(text):
    section_titles = []
    lines = text.split('\n')
    for line in lines:
        clean = line.strip()
        if clean and len(clean.split()) <= 8 and clean[0].isupper():
            section_titles.append(clean)
    return list(dict.fromkeys(section_titles))  # remove duplicates

def find_section_snippet(text, keyword):
    idx = text.lower().find(keyword.lower())
    if idx != -1:
        return text[max(0, idx - 100):idx + 300].replace('\n', ' ').strip()
    return ""

def process_pdf(pdf_path, persona, job, max_pages=5):
    extracted = []
    analysis = []
    try:
        doc = fitz.open(pdf_path)
        pages = min(len(doc), max_pages)
        text = "\n".join([doc[i].get_text() for i in range(pages)])
        if not text.strip():
            return [], []

        sections = extract_sections(text)
        for rank, title in enumerate(sections[:5], 1):
            snippet = find_section_snippet(text, title)
            page_num = 1
            for i in range(pages):
                if title.lower() in doc[i].get_text().lower():
                    page_num = i + 1
                    break

            extracted.append({
                "document": pdf_path.name,
                "section_title": title,
                "importance_rank": rank,
                "page_number": page_num
            })
            analysis.append({
                "document": pdf_path.name,
                "refined_text": snippet,
                "page_number": page_num
            })
    except Exception as e:
        print(f"[!] Failed: {pdf_path.name} -> {e}")
    return extracted, analysis

def process_collection(collection_path):
    input_json_path = collection_path / "challenge1b_input.json"
    output_json_path = collection_path / "challenge1b_output.json"
    pdf_folder = collection_path / "PDFs"

    with open(input_json_path) as f:
        input_data = json.load(f)

    persona = input_data.get("persona")
    job = input_data.get("job_to_be_done")

    input_documents = [f.name for f in pdf_folder.glob("*.pdf")]
    extracted_sections = []
    subsection_analysis = []

    def wrapper(pdf_name):
        return process_pdf(pdf_folder / pdf_name, persona, job)

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(wrapper, input_documents))

    for sec, sub in results:
        extracted_sections.extend(sec)
        subsection_analysis.extend(sub)

    output_data = {
        "metadata": {
            "input_documents": input_documents,
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": str(datetime.datetime.now())
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_json_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"[✓] Processed {collection_path.name}")

def main():
    root = Path("/app")
    for collection in root.iterdir():
        if collection.is_dir() and collection.name.lower().startswith("collection"):
            process_collection(collection)

if __name__ == "__main__":
    main()
