# 📄 **PDF Outline Extractor – Adobe India Hackathon 2025**

## 🚀 **Build Docker Image**
Run this from your project root:
```bash
docker build --platform linux/amd64 -t pdf-outline-extractor .
▶Run Container
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outline-extractor
📄 View Output
After execution, check:
ls output/
cat output/yourfile.json
🛠️ Technical Approach
This solution programmatically reconstructs the document outline of a PDF by analyzing its visual typography and layout metadata. Unlike naive text extractors, it uses low-level font properties and page geometry to infer the document’s logical structure.

🔹 Text Parsing and Metadata Extraction
Built on PyMuPDF (fitz), which parses PDFs at the span level, exposing:

📏 Font size

📝 Font name (e.g., Bold, Italic)

⚡ Style flags (bitwise indicators for emphasis)

🖼️ Bounding boxes (for spatial analysis)

✅ This avoids OCR overhead, ensuring fast CPU-only execution.

🔹 Heading Hierarchy Detection
A relative thresholding algorithm dynamically scales heading detection per document:

H1 ≥ 75% of the largest font size

H2 ≥ 60% of the largest font size

H3 ≥ 50% of the largest font size

Additional features:

🏷️ Title detection: First occurrence ≥ 95% of maximum font size

🔠 Style enhancement: Bold/italic detection influences heading confidence scores

🔹 Vertical and Multilingual Support
🌍 Unicode-aware extraction handles multilingual scripts (Chinese, Japanese, etc.)

🔄 A vertical orientation detector (bounding box aspect ratio) flags rotated/vertical text for reconstruction before heading classification

🔹 Structured JSON Output
Generates a JSON with heading level, text, page number, and style attributes:

json

Edit
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1, "style": "bold" }
  ]
}
