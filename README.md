
# PDF Heading Extraction – Process Overview (Adobe Hackathon Round 1A)

1. The process begins with a set of one or more PDF documents placed in the `input/` folder.

2. Each document is opened and the first page is scanned to identify the most prominent text (by size), which is assumed to be the document title.

3. The script then processes every page and analyzes each line of text to identify potential section headings using visual and positional features:
   - Font size: larger text is more likely to be a heading  
   - Bold fonts: indicates higher importance  
   - Uppercase or all-caps lines  
   - Center-aligned text  
   - Numbered patterns (e.g., “1. Introduction”, “(a) Scope”)  
   - Text ending with a colon (:)  

4. Each line that meets at least one of the above criteria is scored and saved as a potential heading candidate.

5. After gathering all heading candidates:
   - The most frequently used font sizes are analyzed.
   - The top three unique sizes are assigned heading levels:
     - Largest → H1  
     - Next largest → H2  
     - Third largest → H3  

6. Duplicate headings (same text on the same page) are filtered out.

7. The final list of headings is cleaned and sorted:
   - First by heading level (H1, H2, H3)
   - Then by page number

8. The result is saved as a structured JSON file in `output/` with this format:
   - The document’s title (from step 2)
   - An ordered outline of headings with their level and page number

9. This process repeats for every PDF in the `input/` directory, producing one JSON output per document.

---

## Other Things —–––––>

==============================  
1 – Technical Overview  
==============================

- No machine learning models are used  
- Works entirely offline  
- Supports multilingual text (including non-English scripts)  
- Lightweight and fast  
- Text extracted using PyMuPDF (`fitz`)  
- Works well across document formats and styles  

==============================  
2 – Output Format  
==============================

Each output file is a JSON structured like this:

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "Scope", "page": 2 },
    { "level": "H3", "text": "Goals", "page": 3 }
  ]
}
```

==============================  
3 – How to Run  
==============================

▶ **Option 1: Run Locally (Python environment)**

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Place PDFs inside the `input/` folder

3. Run:
   ```bash
   python main.py
   ```

4. Output JSONs will be saved in the `output/` folder

▶ **Option 2: Run using Docker**

1. Build the Docker image:
   ```bash
   docker build -t heading-extractor .
   ```

2. Run the container with volume mounts (Windows CMD example):
   ```bash
   docker run --rm ^
     -v "%cd%\input":/app/input ^
     -v "%cd%\output":/app/output ^
     heading-extractor
   ```

   On Mac/Linux, use:
   ```bash
   docker run --rm \
     -v "$PWD/input":/app/input \
     -v "$PWD/output":/app/output \
     heading-extractor
   ```

3. Output will be saved in your local `output/` directory.

==============================  
4 – Use Case Examples  
==============================

- **Document**: Company Strategy Deck  
  → Extracts outline showing Executive Summary, Goals, Financials, etc.

- **Document**: Textbook Chapter (e.g., Organic Chemistry)  
  → Detects all major topics, subtopics, and numbered sections

- **Document**: Government Policy PDF  
  → Builds a navigable table of contents for legal, technical, or public policy documents
