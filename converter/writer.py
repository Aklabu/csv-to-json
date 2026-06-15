import json
from pathlib import Path
from typing import Iterator


"""
Write data to a JSON file in a single operation. Suitable for data that fits
comfortably in memory, with optional indentation for readable output.
"""
def write_json(data: list[dict] | dict, path: Path, indent: int = 4) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

    print(f"   Saved → {path}")


"""
Stream rows to a JSON file without loading all data into memory. Ideal for
large datasets, writing records incrementally and returning the total number
of rows written.
"""
def write_json_stream(rows: Iterator[dict], path: Path, indent: int = 4) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pad = " " * indent
    count = 0

    with open(path, "w", encoding="utf-8") as f:
        f.write("[\n")
        # buffer one line so we can avoid a trailing comma on the last row
        prev_line = None

        for row in rows:
            line = pad + json.dumps(row, ensure_ascii=False, default=str)
            if prev_line is not None:
                f.write(prev_line + ",\n")
            prev_line = line
            count += 1

        # write the last row without a trailing comma
        if prev_line is not None:
            f.write(prev_line + "\n")

        f.write("]")

    print(f"   Saved → {path}  ({count} rows, streamed)")
    return count