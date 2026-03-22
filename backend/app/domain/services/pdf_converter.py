"""PDF-to-CSV conversion pipeline using OCR.

Converts voter PDF files to structured CSV data by:
1. Converting PDF pages to images (skipping first 2 cover pages)
2. Detecting voter card boxes via contour detection
3. Running OCR (Tesseract) on each box
4. Extracting structured fields (name, EPIC, age, gender, etc.)
5. Returning a pandas DataFrame ready for graph ingestion

Optimisations over v1:
- Regex patterns pre-compiled at module level (not per-call)
- PDF pages converted in one batch call (pdf2image handles threading internally)
- Single persistent ThreadPoolExecutor across all pages (no per-page spin-up)
- np.array() / PIL conversion called once per image, result reused across
  detect_boxes + extract_header_text
- Preprocessing (resize + threshold) factored into one helper, called once per box
- process_single_box receives a pre-converted BGR ndarray, not a PIL image
- Header re-parsed only when OCR text actually changes between pages
- _DNE sentinel defined once; dict-comprehension replaces repeated literal assignment
- Gender check tests Female before Male (avoids "female" matching _RE_MALE)
"""

from __future__ import annotations

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import cv2
import numpy as np
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# ── Pre-compiled patterns (module-level — compiled once, reused everywhere) ───

_RE_NAME = re.compile(r"(?:name|नाम)\s*[:\-]?\s*(.+)", re.IGNORECASE)
_RE_RELATION = re.compile(
    r"(father|husband|mother|others|guardian|पिता|पति|माता)", re.IGNORECASE
)
_RE_REL_VALUE = re.compile(r":\s*(.+)")
_RE_AGE = re.compile(r"(?:age|आयु)\s*[:\-]?\s*(\d+)", re.IGNORECASE)
_RE_FEMALE = re.compile(r"(?:female|महिला)", re.IGNORECASE)
_RE_MALE = re.compile(r"(?:male|पुरुष)", re.IGNORECASE)
_RE_EPIC = re.compile(r"[A-Z]{3}\s*\d{6,8}")
_RE_EPIC_VALID = re.compile(r"^[A-Z]{3}\d{7}$")
_RE_HOUSE = re.compile(r"(?:house|मकान)", re.IGNORECASE)
_RE_HOUSE_NUM = re.compile(r"\b\d+\b")
_RE_ASSEMBLY = re.compile(r"Assembly.*?:\s*(.+)", re.IGNORECASE)
_RE_SECTION = re.compile(r"Section.*?:\s*(.+)", re.IGNORECASE)
_RE_PART = re.compile(r"Part\s*No\.?\s*[:\-]?\s*(\d+)", re.IGNORECASE)
_RE_NAME_PREFIX = re.compile(r"^(.{1,3}\s*[:\-]\s*)")
_RE_NAME_LEAD = re.compile(r"^[^a-zA-Z\u0900-\u097F]+")
_RE_NAME_CHARS = re.compile(r"[^a-zA-Z\u0900-\u097F\s\.]")
_RE_CAMEL = re.compile(r"([a-z])([A-Z])")
_RE_SPACED_CAPS = re.compile(r"^([A-Z]\s+){3,}")
_RE_WHITESPACE = re.compile(r"\s+")

_RELATION_MAP = {
    "father": "Father", "पिता": "Father",
    "husband": "Husband", "पति": "Husband",
    "mother": "Mother", "माता": "Mother",
    "others": "Others",
}

_DNE = "UNKNOWN"   # sentinel — "Does Not Exist / not found"

# ── Image helpers ─────────────────────────────────────────────────────────────


def _to_bgr(pil_image) -> np.ndarray:
    """Convert a PIL image to a BGR ndarray once; callers reuse the result."""
    return cv2.cvtColor(np.asarray(pil_image), cv2.COLOR_RGB2BGR)


def _preprocess(bgr: np.ndarray) -> np.ndarray:
    """
    Binarise a BGR crop for Tesseract.
    Called once per box; the result is passed directly to ocr_box.
    """
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    return cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2,
    )

# ── PDF loading ───────────────────────────────────────────────────────────────


def pdf_to_images(pdf_path: str) -> list:
    """Convert PDF to PIL images, skipping first 2 cover pages."""
    return convert_from_path(pdf_path, first_page=3, thread_count=4)

# ── Box detection ─────────────────────────────────────────────────────────────


def detect_boxes(bgr: np.ndarray) -> list[np.ndarray]:
    """
    Detect voter card boxes from a BGR ndarray.
    Accepts the already-converted array from _to_bgr so no second conversion
    is needed. Returns crops sorted top-to-bottom.
    """
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 250 < w < 1000 and 180 < h < 500:
            boxes.append((y, bgr[y:y + h, x:x + w]))

    boxes.sort(key=lambda b: b[0])
    return [crop for _, crop in boxes]

# ── OCR ───────────────────────────────────────────────────────────────────────


def ocr_box(preprocessed: np.ndarray) -> str:
    """Run Tesseract on an already-preprocessed (binarised grayscale) ndarray."""
    return pytesseract.image_to_string(
        Image.fromarray(preprocessed),
        lang="eng+hin",
        config="--oem 3 --psm 11",
    )


def extract_header_text(bgr: np.ndarray) -> str:
    """OCR the top 15 % of a page BGR array for assembly/section/part metadata."""
    h = bgr.shape[0]
    crop = cv2.cvtColor(bgr[0:int(h * 0.15), :], cv2.COLOR_BGR2RGB)
    return pytesseract.image_to_string(
        Image.fromarray(crop), lang="eng+hin", config="--psm 6"
    )

# ── Parsing ───────────────────────────────────────────────────────────────────


def parse_header(text: str) -> dict:
    """Extract assembly, section, part_no from page-header OCR text."""
    def _get(pattern: re.Pattern, fallback: str = _DNE) -> str:
        m = pattern.search(text)
        return _RE_WHITESPACE.sub("", m.group(1).strip()) if m else fallback

    return {
        "assembly": _get(_RE_ASSEMBLY),
        "section": _get(_RE_SECTION),
        "part_no": _get(_RE_PART),
    }


def clean_name(raw: str) -> str:
    """Strip OCR noise from a person's name field."""
    name = _RE_NAME_PREFIX.sub("", raw)
    name = _RE_NAME_LEAD.sub("", name)
    name = _RE_NAME_CHARS.sub("", name)
    if _RE_SPACED_CAPS.match(name):
        name = name.replace(" ", "")
    name = _RE_CAMEL.sub(r"\1 \2", name)
    return " ".join(name.split())


def extract_fields(text: str) -> dict:
    """Extract structured voter fields from OCR text of a single card box."""
    data = {k: _DNE for k in (
        "epic", "name", "relation_name", "relation_type",
        "house_no", "age", "gender",
    )}

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    full = " ".join(lines)

    # NAME
    for line in lines:
        m = _RE_NAME.search(line)
        if m:
            data["name"] = clean_name(m.group(1).strip())
            break

    # RELATION
    for line in lines:
        rel = _RE_RELATION.search(line)
        if rel:
            val_m = _RE_REL_VALUE.search(line)
            if val_m:
                data["relation_type"] = _RELATION_MAP.get(rel.group(1).lower(), "Other")
                data["relation_name"] = clean_name(val_m.group(1).strip())
            break

    # HOUSE NUMBER
    for line in lines:
        if _RE_HOUSE.search(line):
            m = _RE_HOUSE_NUM.search(line)
            if m:
                data["house_no"] = m.group(0)
            break

    # AGE
    m = _RE_AGE.search(full)
    if m:
        data["age"] = m.group(1)

    # GENDER — Female checked first; its string contains "male" as a substring
    if _RE_FEMALE.search(full):
        data["gender"] = "Female"
    elif _RE_MALE.search(full):
        data["gender"] = "Male"

    # EPIC
    m = _RE_EPIC.search(full)
    if m:
        data["epic"] = m.group(0).replace(" ", "")

    return data


def clean_record(data: dict) -> dict:
    """Validate field values; reset out-of-range or malformed entries to DNE."""
    if data["epic"] != _DNE and not _RE_EPIC_VALID.match(data["epic"]):
        data["epic"] = _DNE

    if data["age"] != _DNE:
        try:
            if not (18 <= int(data["age"]) <= 100):
                data["age"] = _DNE
        except ValueError:
            data["age"] = _DNE

    if data["name"] != _DNE and len(data["name"]) < 3:
        data["name"] = _DNE

    return data

# ── Per-box worker ────────────────────────────────────────────────────────────


def process_single_box(box_bgr: np.ndarray, header_data: dict) -> dict | None:
    """
    Full processing for one voter card box.
    Receives a BGR ndarray (converted once upstream) and a header dict.
    Thread-safe — operates on local state only.
    """
    text = ocr_box(_preprocess(box_bgr))
    text = text.replace("Photo Available", "").replace("|", "")

    if len(text.strip()) < 20:
        return None

    record = clean_record(extract_fields(text))

    if record["name"] == _DNE:
        return None

    record.update(header_data)
    return record

# ── Main pipeline ─────────────────────────────────────────────────────────────


def process_pdf(pdf_path: str) -> pd.DataFrame:
    """Full pipeline: PDF path → structured DataFrame.

    Args:
        pdf_path: Path to the voter PDF file.

    Returns:
        pandas.DataFrame with columns matching voters.csv schema.
    """
    print(f"Processing: {pdf_path}")
    images = pdf_to_images(pdf_path)

    all_records: list[dict] = []
    prev_header_text: str | None = None
    cached_header: dict = {}

    # One executor for the entire PDF — eliminates per-page thread pool spin-up
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        for page_num, pil_img in enumerate(images):
            print(f"\nPage {page_num + 3}", end=" — ", flush=True)

            # Convert PIL → BGR once; both detect_boxes and extract_header_text reuse it
            bgr = _to_bgr(pil_img)

            # Re-parse header only when the OCR text actually differs from the last page
            header_text = extract_header_text(bgr)
            if header_text != prev_header_text:
                cached_header = parse_header(header_text)
                prev_header_text = header_text

            boxes = detect_boxes(bgr)
            print(f"{len(boxes)} boxes found", flush=True)

            if not boxes:
                continue

            futures = {
                executor.submit(process_single_box, box, cached_header): i
                for i, box in enumerate(boxes)
            }
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    all_records.append(result)

    df = pd.DataFrame(all_records).fillna(_DNE)
    print(f"\nDone. Records extracted: {len(df)}")
    return df
