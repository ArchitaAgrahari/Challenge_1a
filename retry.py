import os
import fitz  # PyMuPDF
import json
import re
from collections import Counter

# Paths
INPUT_DIR = "Challenge_1a/sample_dataset/pdfs"
OUTPUT_DIR = "Challenge_1a/sample_dataset/outputs"

# Patterns considered as noise
NOISE_PATTERNS = [
    re.compile(r"^\d+(\.|-)?$"),                      # 1. or 2-
    re.compile(r"^\d{1,2} [A-Z]{3,} \d{4}$"),          # 18 JUNE 2013
    re.compile(r"^page \d+$", re.IGNORECASE),         # Page 3
    re.compile(r"^http"),                             # URLs
    re.compile(r"^\s*$")                              # Empty lines
]

def clean(text):
    return re.sub(r"\s+", " ", text.strip())

def is_noise(text, frequency):
    if frequency > 2:
        return True
    for pattern in NOISE_PATTERNS:
        if pattern.match(text):
            return True
    return False

def is_structured(text):
    return bool(re.match(r"^\d+(\.\d+)*\s+.+", text))

def is_heading_candidate(text, size, max_size, is_bold, is_italic):
    word_count = len(text.split())

    # Reject long lines
    if word_count > 25:
        return False

    # Reject very short lines unless they are styled
    if len(text) < 2 or is_noise(text, 1):
        return False

    # Accept short, styled one-word headings
    if word_count == 1 and (is_bold or is_italic) and size >= 0.6 * max_size:
        return True

    # Generic bold/italic headings
    if (is_bold or (is_bold and is_italic)) :
        return True

    # Also accept if nearly title-size
    if size >= 0.9 * max_size:
        return True

    return False

def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = []
    sizes = []
    counter = Counter()

    for pno, page in enumerate(doc, 1):
        page_blocks = page.get_text("dict")["blocks"]
        for block in page_blocks:
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                line_text = clean(" ".join(span["text"] for span in spans))
                if not line_text:
                    continue

                size = max(span["size"] for span in spans)
                fonts = [span["font"] for span in spans if "font" in span]
                is_bold = any("bold" in f.lower() for f in fonts)
                is_italic = any("italic" in f.lower() or "oblique" in f.lower() for f in fonts)

                sizes.append(size)
                counter[line_text.lower()] += 1

                blocks.append({
                    "text": line_text,
                    "font_size": size,
                    "font_names": fonts,
                    "is_bold": is_bold,
                    "is_italic": is_italic,
                    "page": pno
                })

    return blocks, sizes, counter

def extract_headings(blocks, sizes, counter):
    title = ""
    headings = []
    seen = set()
    max_size = max(sizes) if sizes else 0

    for block in blocks:
        text = block["text"]
        lowered = text.lower()

        if lowered in seen or is_noise(text, counter[lowered]):
            continue
        seen.add(lowered)

        # Skip structured form fields like "12. Amount ..." if short
        if is_structured(text) and len(text.split()) <= 4:
            continue

        if not title and block["page"] == 1 and block["font_size"] >= 0.95 * max_size:
            title = text
            continue

        if is_structured(text):
            headings.append({
                "level": "H1",
                "text": text,
                "page": block["page"]
            })
        elif is_heading_candidate(text, block["font_size"], max_size, block["is_bold"], block["is_italic"]):
            headings.append({
                "level": "H2",
                "text": text,
                "page": block["page"]
            })

    return title, headings

def process_pdf(pdf_file):
    path = os.path.join(INPUT_DIR, pdf_file)
    blocks, sizes, counter = extract_text_blocks(path)
    title, headings = extract_headings(blocks, sizes, counter)
    return {
        "title": title,
        "outline": headings
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fname in os.listdir(INPUT_DIR):
        if fname.lower().endswith(".pdf"):
            print(f"Processing: {fname}")
            result = process_pdf(fname)
            out_path = os.path.join(OUTPUT_DIR, fname.replace(".pdf", ".json"))
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Saved to: {out_path}")

if __name__ == "__main__":
    main()
