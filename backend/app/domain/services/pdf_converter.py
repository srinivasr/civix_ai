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
_RE_SECTION = re.compile(
    r"Section\s+No\s+and\s+Name\s+(.+)",
    re.IGNORECASE
)
_RE_NAME_PREFIX = re.compile(r"^(.{1,3}\s*[:\-]\s*)")
_RE_NAME_LEAD = re.compile(r"^[^a-zA-Z\u0900-\u097F]+")
_RE_NAME_CHARS = re.compile(r"[^a-zA-Z\u0900-\u097F\s\.]")
_RE_CAMEL = re.compile(r"([a-z])([A-Z])")
_RE_SPACED_CAPS = re.compile(r"^([A-Z]\s+){3,}")
_RE_WHITESPACE = re.compile(r"\s+")

_RE_AC_FIRST_PAGE = re.compile(r"Assembly Constituency.*?(\d+)", re.IGNORECASE)
_RE_BOOTH_FIRST_PAGE = re.compile(r"Polling Station.*?(\d+)", re.IGNORECASE)

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
    crop = cv2.cvtColor(bgr[0:int(h * 0.25), :], cv2.COLOR_BGR2RGB)
    return pytesseract.image_to_string(
        Image.fromarray(crop), lang="eng+hin", config="--psm 6"
    )

# ── Parsing ───────────────────────────────────────────────────────────────────


def parse_header(text: str) -> dict:
    """Extract assembly and section from page-header OCR text."""
    def _get(pattern: re.Pattern, fallback: str = _DNE) -> str:
        m = pattern.search(text)
        return _RE_WHITESPACE.sub("", m.group(1).strip()) if m else fallback

    return {
        "assembly": _get(_RE_ASSEMBLY),
        "section": _get(_RE_SECTION),
    }

def get_state_code(state):
    state = state.lower()

    state = state.lower().strip()

    # 🔥 OCR noise cleaning (IMPORTANT)
    state = state.replace("u05", "").replace("u0s", "")
    state = state.replace("s14", "").replace("s26", "")
    state = state.strip()

    # English + Hindi matching
    if "mahar" in state or "महार" in state: return "MH"
    elif "uttar pradesh" in state or "उत्तर" in state: return "UP"
    elif "bihar" in state or "बिहार" in state: return "BR"
    elif "gujarat" in state or "गुजरात" in state: return "GJ"
    elif "rajasthan" in state or "राजस्थान" in state: return "RJ"
    elif "madhya" in state or "मध्य" in state: return "MP"
    elif "karnataka" in state or "कर्नाटक" in state: return "KA"
    elif "tamil" in state or "तमिल" in state: return "TN"
    elif "telangana" in state or "तेलंगाना" in state: return "TS"
    elif "west bengal" in state or "बंगाल" in state: return "WB"
    elif "kerala" in state or "केरल" in state: return "KL"
    elif "odisha" in state or "ओडिशा" in state: return "OR"
    elif "punjab" in state or "पंजाब" in state: return "PB"
    elif "assam" in state or "असम" in state: return "AS"
    elif "jharkhand" in state or "झारखंड" in state: return "JH"
    elif "chhattisgarh" in state or "छत्तीसगढ़" in state: return "CG"
    elif "haryana" in state or "हरियाणा" in state: return "HR"
    elif "himachal" in state or "हिमाचल" in state: return "HP"
    elif "uttarakhand" in state or "उत्तराखंड" in state: return "UK"
    elif "goa" in state or "गोवा" in state: return "GA"
    elif "tripura" in state or "त्रिपुरा" in state: return "TR"
    elif "manipur" in state or "मणिपुर" in state: return "MN"
    elif "meghalaya" in state or "मेघालय" in state: return "ML"
    elif "mizoram" in state or "मिजोरम" in state: return "MZ"
    elif "nagaland" in state or "नागालैंड" in state: return "NL"
    elif "sikkim" in state or "सिक्किम" in state: return "SK"
    elif "arunachal" in state or "अरुणाचल" in state: return "AR"
    elif "delhi" in state: return "DL"

    return "XX"


def extract_first_page_data(bgr: np.ndarray) -> dict:
    """Extract state, AC number, and booth number from the first page."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    
    text = pytesseract.image_to_string(gray, lang="eng+hin", config="--psm 6")
    text = text.replace("\n", " ")
    text = _RE_WHITESPACE.sub(" ", text)
    
    data = {"state": "", "ac_number": "", "booth_number": ""}
    
    text_lower = text.lower()

    # 🔥 DIRECT STATE DETECTION (ROBUST)
    if "delhi" in text_lower or "nct" in text_lower or "nctofdelhi"  in text_lower or "newdelhi" in text_lower:
        data["state"] = "delhi"

    elif "manipur" in text_lower:
        data["state"] = "manipur"

    elif "sikkim" in text_lower:
        data["state"] = "sikkim"
    elif "maharashtra" in text_lower:
        data["state"] = "mahar"

    # fallback (optional)
    else:
        data["state"] = ""
        
    m_ac = _RE_AC_FIRST_PAGE.search(text)
    if m_ac:
        data["ac_number"] = m_ac.group(1)
        
    m_booth = _RE_BOOTH_FIRST_PAGE.search(text)
    if m_booth:
        data["booth_number"] = m_booth.group(1)
        
    return data


def generate_booth_id(state: str, ac: str, booth: str) -> str:
    """Generate a unique booth ID from state, AC, and booth number."""
    state_code = get_state_code(state)
    booth = booth.zfill(3) if booth else "000"
    return f"{state_code}_{ac}_{booth}"


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
    
    # Extract cover page data for booth ID
    try:
        cover_pages = convert_from_path(pdf_path, first_page=1, last_page=1, thread_count=1)
        booth_id = _DNE
        if cover_pages:
            cover_bgr = _to_bgr(cover_pages[0])
            first_page_data = extract_first_page_data(cover_bgr)
            booth_id = generate_booth_id(
                first_page_data["state"],
                first_page_data["ac_number"],
                first_page_data["booth_number"]
            )
            print(f"Booth ID: {booth_id}")
    except Exception as e:
        print(f"Failed to extract cover page: {e}")
        booth_id = _DNE

    images = pdf_to_images(pdf_path)

    all_records: list[dict] = []
    prev_header_text: str | None = None
    cached_header: dict = {"booth_id": booth_id}

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
                cached_header["booth_id"] = booth_id
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