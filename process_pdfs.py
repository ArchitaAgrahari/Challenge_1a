import os
import fitz  # PyMuPDF
import json
import re
from collections import Counter

# Directories (please update as per your setup)
INPUT_DIR = "Challenge_1a\sample_dataset\pdfs"  # Path to PDF input folder
OUTPUT_DIR = "Challenge_1a\sample_dataset\outputs"  # Path where JSON outputs will be saved

# Regex to detect numbered headings like "1", "2.1", "3.2.1"
NUMERIC_HEADING_RE = re.compile(r"^(\d+(\.\d+)*)(\.|\s)(.*)")

def clean(text):
    """Normalize and clean text lines."""
    return re.sub(r'\s+', ' ', text.strip())

def get_heading_level(numbering):
    """Return heading level based on count of dots — e.g., 2.1 -> level 2 (H2)."""
    return numbering.count('.') + 1 if numbering else 1

def extract_blocks(pdf_path):
    """Extract blocks of text from PDF along with font size and styling info."""
    doc = fitz.open(pdf_path)
    blocks = []
    font_sizes = []
    freq_counter = Counter()

    for page_index, page in enumerate(doc):  # page_index is zero-based
        page_blocks = page.get_text("dict")["blocks"]
        for block in page_blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = clean(" ".join(span["text"] for span in spans if span["text"].strip()))
                if not text:
                    continue

                size = max(span["size"] for span in spans)
                fonts = [span["font"] for span in spans]
                is_bold = any("bold" in f.lower() for f in fonts)
                is_italic = any("italic" in f.lower() or "oblique" in f.lower() for f in fonts)
                # Approximate vertical position (top of line)
                y0 = spans[0]["bbox"][1] if spans else 0

                blocks.append({
                    "text": text,
                    "size": size,
                    "page": page_index,
                    "is_bold": is_bold,
                    "is_italic": is_italic,
                    "y0": y0,
                })

                font_sizes.append(size)
                freq_counter[text.lower()] += 1

    return blocks, font_sizes, freq_counter

def is_heading_candidate(text, size, body_size, is_bold, is_italic):
    """Determine if a line is a heading based on text length, size, style, and numbering."""
    if not text or len(text) < 4 or len(text) > 120:
        return False
    if size < body_size + 1 and not NUMERIC_HEADING_RE.match(text):
        return False
    if text.isupper() and not NUMERIC_HEADING_RE.match(text):
        return False
    # Exclude lines indicating versions and copyright info
    if any(x in text.lower() for x in ["version", "copyright", "all rights reserved"]):
        return False
    return is_bold or is_italic or NUMERIC_HEADING_RE.match(text)

def classify_level(text, size, body_size, font_sizes_list):
    """Assign heading level using numbering or font size hierarchy."""
    m = NUMERIC_HEADING_RE.match(text)
    if m:
        numbering = m.group(1)
        return "H" + str(get_heading_level(numbering))

    # For non-numbered headings, use font size clustering heuristic
    sorted_sizes = sorted(set(font_sizes_list), reverse=True)
    for idx, fs in enumerate(sorted_sizes):
        if abs(size - fs) < 0.5:
            return "H" + str(idx + 1)

    # Default to H3 if no match found
    return "H3"

def extract_headings(blocks, font_sizes):
    """Derive the document title and outline of headings from blocks."""
    outline = []
    seen = set()

    if not font_sizes:
        return "", []

    # Determine typical body font size (mode of font sizes)
    font_size_counts = Counter(font_sizes)
    body_size = font_size_counts.most_common(1)[0][0]

    title_candidate = None

    for block in blocks:
        text = block["text"].rstrip()
        page = block["page"]
        size = block["size"]
        is_bold = block["is_bold"]
        is_italic = block["is_italic"]
        y0 = block.get("y0", 0)

        key = (text.lower(), page)
        if key in seen:
            continue
        seen.add(key)

        # Identify document title — first big non-heading line on first page
        if page == 0 and not title_candidate and size > body_size + 1 and not is_heading_candidate(text, size, body_size, is_bold, is_italic):
            title_candidate = text
            continue

        # Skip the title line from headings
        if title_candidate and text == title_candidate and page == 0:
            continue

        # Determine if this block is a heading
        if not is_heading_candidate(text, size, body_size, is_bold, is_italic):
            continue

        # Assign heading level based on numbering or font sizes
        level = classify_level(text, size, body_size, font_sizes)

        outline.append({
            "level": level,
            "text": text + (" " if not text.endswith(" ") else ""),
            "page": page,
            "y0": y0
        })

    # Sort headings by page and vertical position
    outline.sort(key=lambda x: (x["page"], x["y0"]))

    # Remove position info before output
    for heading in outline:
        heading.pop("y0", None)

    # If no title candidate, fallback to first heading
    if not title_candidate and outline:
        title_candidate = outline[0]["text"]
        outline = outline[1:]

    return title_candidate.strip(), outline

def process_pdf(pdf_path):
    blocks, font_sizes, freq_counter = extract_blocks(pdf_path)
    title, outline = extract_headings(blocks, font_sizes)
    return {"title": title, "outline": outline}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_files = sorted(f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf"))
    for pdf_file in pdf_files:
        try:
            pdf_path = os.path.join(INPUT_DIR, pdf_file)
            print(f"Processing {pdf_file}...")
            result = process_pdf(pdf_path)
            output_path = os.path.join(OUTPUT_DIR, pdf_file.replace(".pdf", ".json"))
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Saved {output_path}")
        except Exception as e:
            print(f"Failed to process {pdf_file}: {e}")

if __name__ == "__main__":
    main()
