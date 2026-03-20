"""PDF-to-CSV conversion pipeline using OCR.

Converts voter PDF files to structured CSV data by:
1. Converting PDF pages to images (skipping first 2 cover pages)
2. Detecting voter card boxes via contour detection
3. Running OCR (Tesseract) on each box
4. Extracting structured fields (name, EPIC, age, gender, etc.)
5. Returning a pandas DataFrame ready for graph ingestion
"""

from pdf2image import convert_from_path
import pytesseract
import pandas as pd
import re
import cv2
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image


def pdf_to_images(pdf_path):
    """Convert PDF to list of PIL images, skipping first 2 cover pages."""
    return convert_from_path(pdf_path, first_page=3, thread_count=4)


def detect_boxes(image):
    """Detect voter card boxes on a page image via contour detection."""
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 250 < w < 1000 and 180 < h < 500:
            crop = img[y:y + h, x:x + w]
            boxes.append((y, crop))

    boxes = sorted(boxes, key=lambda b: b[0])
    return [b[1] for b in boxes]


def ocr_box(image):
    """Run OCR on a single voter card box image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2,
    )
    pil_img = Image.fromarray(gray)
    text = pytesseract.image_to_string(
        pil_img, lang="eng+hin", config="--oem 3 --psm 11"
    )
    return text


def extract_header(image):
    """Extract header text (assembly, section, part_no) from top of page."""
    img = np.array(image)
    h, w = img.shape[:2]
    header_img = img[0:int(h * 0.15), :]
    pil_img = Image.fromarray(header_img)
    text = pytesseract.image_to_string(
        pil_img, lang="eng+hin", config="--psm 6"
    )
    return text


def parse_header(text):
    """Parse assembly, section, part_no from header OCR text."""
    header = {
        "assembly": "DNE",
        "section": "DNE",
        "part_no": "DNE",
    }

    match = re.search(r"Assembly.*?:\s*(.+)", text, re.IGNORECASE)
    if match:
        header["assembly"] = match.group(1).strip()

    match = re.search(r"Section.*?:\s*(.+)", text, re.IGNORECASE)
    if match:
        header["section"] = match.group(1).strip()

    match = re.search(r"Part\s*No\.?\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
    if match:
        header["part_no"] = match.group(1)

    header["assembly"] = re.sub(r"\s+", "", header["assembly"])
    header["section"] = re.sub(r"\s+", "", header["section"])

    return header


def clean_name(name):
    """Clean OCR noise from a person's name."""
    name = re.sub(r'^(.{1,3}\s*[:\-]\s*)', '', name)
    name = re.sub(r'^[^a-zA-Z\u0900-\u097F]+', '', name)
    name = re.sub(r'[^a-zA-Z\u0900-\u097F\s\.]', '', name)

    if re.match(r'^([A-Z]\s+){3,}', name):
        name = name.replace(" ", "")

    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    return " ".join(name.split())


def extract_fields(text):
    """Extract structured voter fields from OCR text of a single box."""
    data = {
        "epic": "DNE",
        "name": "DNE",
        "relation_name": "DNE",
        "relation_type": "DNE",
        "house_no": "DNE",
        "age": "DNE",
        "gender": "DNE",
    }

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    full_text = " ".join(lines)

    # NAME
    for line in lines:
        if re.search(r"(name|नाम)", line, re.IGNORECASE):
            match = re.search(
                r"(name|नाम)\s*[:\-]?\s*(.+)", line, re.IGNORECASE
            )
            if match:
                data["name"] = clean_name(match.group(2).strip())
                break

    # RELATION
    rel_pattern = (
        r"(father|husband|mother|others|guardian|पिता|पति|माता)"
    )
    for line in lines:
        if re.search(rel_pattern, line, re.IGNORECASE):
            rel = re.search(rel_pattern, line, re.IGNORECASE)
            name = re.search(r":\s*(.+)", line)
            if rel and name:
                val = rel.group(1).lower()
                if val in ["father", "पिता"]:
                    data["relation_type"] = "Father"
                elif val in ["husband", "पति"]:
                    data["relation_type"] = "Husband"
                elif val in ["mother", "माता"]:
                    data["relation_type"] = "Mother"
                elif val in ["others"]:
                    data["relation_type"] = "Others"
                else:
                    data["relation_type"] = "Other"
                data["relation_name"] = clean_name(name.group(1).strip())
                break

    # HOUSE
    for line in lines:
        if re.search(r"(house|मकान)", line, re.IGNORECASE):
            match = re.search(r"\b\d+\b", line)
            if match:
                data["house_no"] = match.group(0)
                break

    # AGE
    age = re.search(
        r"(age|आयु)\s*[:\-]?\s*(\d+)", full_text, re.IGNORECASE
    )
    if age:
        data["age"] = age.group(2)

    # GENDER
    if re.search(r"(female|महिला)", full_text, re.IGNORECASE):
        data["gender"] = "Female"
    elif re.search(r"(male|पुरुष)", full_text, re.IGNORECASE):
        data["gender"] = "Male"

    # EPIC
    epic_match = re.search(r"[A-Z]{3}\s*\d{6,8}", full_text)
    if epic_match:
        data["epic"] = epic_match.group(0).replace(" ", "")

    for k, v in data.items():
        if not v or v.strip() == "":
            data[k] = "DNE"

    return data


def clean_record(data):
    """Validate and clean a single voter record."""
    if data["epic"] != "DNE" and not re.match(
        r"^[A-Z]{3}\d{7}$", data.get("epic", "")
    ):
        data["epic"] = "DNE"

    if data["age"] != "DNE":
        try:
            age = int(data["age"])
            if age < 18 or age > 100:
                data["age"] = "DNE"
        except ValueError:
            data["age"] = "DNE"

    if data["name"] != "DNE" and len(data["name"]) < 3:
        data["name"] = "DNE"

    return data


def process_single_box(args):
    """Process a single voter card box — thread-safe entry point."""
    box, header_data = args
    text = ocr_box(box)
    text = text.replace("Photo Available", "").replace("|", "")

    if len(text.strip()) < 20:
        return None

    record = extract_fields(text)
    record = clean_record(record)

    record["assembly"] = header_data.get("assembly", "DNE")
    record["section"] = header_data.get("section", "DNE")
    record["part_no"] = header_data.get("part_no", "DNE")

    if record.get("name") != "DNE":
        return record

    return None


def process_pdf(pdf_path):
    """Full pipeline: PDF → structured DataFrame.

    Args:
        pdf_path: Path to the voter PDF file.

    Returns:
        pandas.DataFrame with columns matching voters.csv schema.
    """
    print(f"Processing: {pdf_path}")
    images = pdf_to_images(pdf_path)

    all_records = []

    for page_num, img in enumerate(images):
        print(f"\nProcessing Page {page_num + 3}")

        header_text = extract_header(img)
        header_data = parse_header(header_text)

        boxes = detect_boxes(img)
        print(f"Boxes found: {len(boxes)}")

        with ThreadPoolExecutor(
            max_workers=os.cpu_count() or 4
        ) as executor:
            batch_results = list(
                executor.map(
                    process_single_box,
                    [(b, header_data) for b in boxes],
                )
            )

        for record in batch_results:
            if record is not None:
                all_records.append(record)

    df = pd.DataFrame(all_records)
    df.fillna("DNE", inplace=True)

    print(f"\nDone. Records extracted: {len(df)}")
    return df
