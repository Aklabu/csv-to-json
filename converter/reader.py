import csv
from pathlib import Path
from typing import Iterator

try:
    # pyrefly: ignore [missing-import]
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

from converter.type_inference import infer_row


# detect file encoding using chardet if available
# falls back to utf-8-sig which handles Excel BOM automatically
def detect_encoding(path: Path) -> str:
    if HAS_CHARDET:
        with open(path, "rb") as f:
            raw = f.read(min(32_768, path.stat().st_size))  # read up to 32KB
        result = chardet.detect(raw)
        encoding = result.get("encoding") or "utf-8-sig"
        confidence = result.get("confidence", 0)
        print(f"   Encoding detected: {encoding} (confidence: {confidence:.0%})")
        return encoding
    return "utf-8-sig"


"""
Yield rows from a CSV file as dictionaries. Reads the CSV file located at
`path`, optionally inferring Python data types for values when `infer_types`
is enabled. If no `encoding` is provided, the file encoding is automatically
detected.
"""
def read_csv(
    path: Path,
    infer_types: bool = False,
    encoding: str = None,
) -> Iterator[dict]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected .csv file, got: {path.suffix}")

    enc = encoding or detect_encoding(path)

    with open(path, newline="", encoding=enc, errors="replace") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError(f"CSV has no headers: {path}")

        for row in reader:
            # strip whitespace from all keys and values
            clean = {k.strip(): v.strip() for k, v in row.items() if k}
            yield infer_row(clean) if infer_types else clean


# return only the header row of a CSV file without reading all rows
def get_headers(path: Path, encoding: str = None) -> list[str]:
    path = Path(path)
    enc = encoding or detect_encoding(path)
    with open(path, newline="", encoding=enc) as f:
        reader = csv.DictReader(f)
        return [h.strip() for h in (reader.fieldnames or [])]