import os
import json
import fitz
import re
import subprocess
from collections import Counter

def translate_with_apertium(text, langpair="ja-en"):
    try:
        process = subprocess.Popen(
            ['apertium', langpair],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(text)
        return stdout.strip() if stdout else text
    except:
        return text

def extract_heading_lines(pdf, document_title):
    headings = []
    seen = set()
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        blocks = page.get_text("dict", flags=11)["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                line_text = " ".join(span["text"].strip() for span in spans).strip()
                if not line_text or line_text in seen:
                    continue
                seen.add(line_text)
                font_size = round(sum(span["size"] for span in spans) / len(spans), 1)
                font_name = spans[0]["font"]
                is_bold = "bold" in font_name.lower()
                clean_text = re.sub(r"\s+", " ", line_text).strip()
                if clean_text.lower() == document_title.lower():
                    continue
                if len(clean_text) < 3 or clean_text.islower() or not any(c.isalpha() for c in clean_text):
                    continue
                is_numbered = re.match(r"^\(?[0-9a-zA-Z]+\)?[.)]?\s+[A-Z]", clean_text)
                is_potential_heading = is_numbered or is_bold or font_size >= 12 or line_text.endswith(":")
                if is_potential_heading:
                    translated = translate_with_apertium(clean_text)
                    headings.append({
                        "text": translated,
                        "size": font_size,
                        "font": font_name,
                        "page": page_num + 1
                    })
    return headings

def determine_heading_levels(headings):
    sizes = [h["size"] for h in headings]
    common_sizes = [size for size, _ in Counter(sizes).most_common(3)]
    common_sizes.sort(reverse=True)
    size_to_level = {}
    if len(common_sizes) > 0:
        size_to_level[common_sizes[0]] = "H1"
    if len(common_sizes) > 1:
        size_to_level[common_sizes[1]] = "H2"
    if len(common_sizes) > 2:
        size_to_level[common_sizes[2]] = "H3"
    result = []
    used = set()
    for h in headings:
        level = size_to_level.get(h["size"])
        key = (h["text"], h["page"])
        if level and key not in used:
            used.add(key)
            result.append({
                "level": level,
                "text": h["text"],
                "page": h["page"]
            })
    return result

def extract_title(pdf):
    first_page = pdf[0]
    blocks = first_page.get_text("dict", flags=11)["blocks"]
    candidates = []
    for block in blocks:
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            line_text = " ".join(span["text"].strip() for span in spans).strip()
            if len(line_text) < 3:
                continue
            font_size = round(sum(span["size"] for span in spans) / len(spans), 1)
            candidates.append((font_size, line_text))
    candidates.sort(reverse=True)
    return candidates[0][1] if candidates else "Untitled"

def parse_single_pdf(path):
    pdf = fitz.open(path)
    title = extract_title(pdf)
    headings = extract_heading_lines(pdf, title)
    outline = determine_heading_levels(headings)
    return {"title": title, "outline": outline}

def process_all_pdfs():
    input_dir = "/app/input"
    output_dir = "/app/output"
    for name in os.listdir(input_dir):
        if name.lower().endswith(".pdf"):
            full_path = os.path.join(input_dir, name)
            result = parse_single_pdf(full_path)
            out_file = os.path.join(output_dir, name.replace(".pdf", ".json"))
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_all_pdfs()
