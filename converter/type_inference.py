from datetime import datetime

# supported date formats to try during type inference
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
]


# cast a raw CSV string to the most appropriate Python type
# order: None -> bool -> int -> float -> date -> str
def infer_type(value: str):
    if not isinstance(value, str):
        return value

    stripped = value.strip()

    # return None for empty or null-like values
    if stripped == "" or stripped.lower() in ("null", "none", "n/a", "na", "-"):
        return None

    # detect truthy boolean strings
    if stripped.lower() in ("true", "yes", "1"):
        return True
    # detect falsy boolean strings
    if stripped.lower() in ("false", "no", "0"):
        return False

    # try casting to integer
    try:
        return int(stripped)
    except ValueError:
        pass

    # try casting to float, handle "1,000.5" style numbers
    try:
        return float(stripped.replace(",", ""))
    except ValueError:
        pass

    # try matching known date formats
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(stripped, fmt).date().isoformat()
        except ValueError:
            continue

    # fall back to plain string
    return stripped


# apply infer_type to every value in a row dict
def infer_row(row: dict) -> dict:
    return {k: infer_type(v) for k, v in row.items()}