# PDF Outline Extractor — Adobe India Hackathon 2025

Welcome to the **Connecting the Dots** challenge solution, designed to transform static PDFs into intelligent, structured documents by extracting clean, hierarchical outlines of titles and headings.

---

## Approach

Our extractor utilizes **layout and typographical cues** to identify document structure rather than plain text parsing:

- **PyMuPDF (fitz)** extracts each line’s text, font size, style (bold/italic), and vertical position.
- **Heading detection** employs a hybrid strategy:
  - Font size thresholds relative to dominant body text size.
  - Recognition of numbered section headings (e.g., "1", "1.1", "1.1.1") to infer heading levels (H1, H2, H3).
  - Bold or italic styling increases confidence of heading candidates.
  - The document title is inferred as the first prominent non-heading line on the first page.
- **Noise filtering** removes page numbers, headers, footers, and common copyright/version text without hardcoded rules.
- Headings are output in **natural reading order**, sorted by page (zero-indexed) and vertical position.

---

## Features

- Processes PDFs with **high accuracy and speed** (under 10 seconds for 50-page documents).
- Fully **offline**, compatible with **AMD64 CPUs**, requiring no GPUs or internet access.
- Supports complex layouts and **multilingual documents**.
- Outputs structured **JSON** files:

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "Background", "page": 2 }
  ]
}
```

- Seamlessly integrates with Round 1B semantic ranking and downstream processing.

---

## Build and Run Instructions

1. **Build Docker image:**

```bash
docker build --platform linux/amd64 -t pdf-outline-extractor .
```

2. **Run Docker container:**

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outline-extractor
```

3. **Access output files:**

```bash
ls output/
cat output/yourfile.json
```

---

## Project Structure

```
/app
├── main.py       # PDF outline extraction code
├── Dockerfile     # Docker container config
├── README.md      # This documentation
/input              # Place PDFs here
/output             # Extracted JSON files appear here
```

---

## Technology Stack

- **PyMuPDF (fitz):** Efficient PDF parsing and layout extraction of font and position metadata.
- **Python Standard Library:** JSON, regex, and file system modules.

---

## Why This Matters

By enabling machines to understand document structure, this solution empowers:

- Enhanced **semantic search and navigation** in large PDF corpora.
- Smarter **content discovery and linking** across documents.
- The foundation for **AI-powered interactive reading experiences**.

Connect the dots. Bring your PDFs to life!

