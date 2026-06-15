import pytest
from pathlib import Path
from converter.reader import read_csv, get_headers


# Helper functions for testing CSV reading.

# Writes a temporary CSV file and returns its path.
def make_csv(tmp_path: Path, filename: str, content: str) -> Path:
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


# Tests for basic CSV reading functionality.

def test_read_csv_returns_correct_row_count(tmp_path):
    f = make_csv(tmp_path, "data.csv", "name,age\nAlice,30\nBob,25\n")
    rows = list(read_csv(f))
    assert len(rows) == 2

def test_read_csv_returns_correct_keys(tmp_path):
    f = make_csv(tmp_path, "data.csv", "name,age,city\nAlice,30,Dhaka\n")
    rows = list(read_csv(f))
    assert set(rows[0].keys()) == {"name", "age", "city"}

def test_read_csv_returns_correct_values(tmp_path):
    f = make_csv(tmp_path, "data.csv", "name,age\nAlice,30\n")
    rows = list(read_csv(f))
    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == "30"  # Expect raw string since type inference is disabled.

# Ensure whitespace around values and headers is correctly stripped.
def test_read_csv_strips_whitespace(tmp_path):
    f = make_csv(tmp_path, "data.csv", " name , age \n Alice , 30 \n")
    rows = list(read_csv(f))
    assert "name" in rows[0]
    assert rows[0]["name"] == "Alice"


# Tests for type inference during reading.

def test_read_csv_with_infer_types_casts_integer(tmp_path):
    f = make_csv(tmp_path, "data.csv", "name,age\nAlice,30\n")
    rows = list(read_csv(f, infer_types=True))
    assert rows[0]["age"] == 30  # Expect cast to integer.

def test_read_csv_with_infer_types_casts_none(tmp_path):
    f = make_csv(tmp_path, "data.csv", "name,score\nAlice,\n")
    rows = list(read_csv(f, infer_types=True))
    assert rows[0]["score"] is None


# Tests for handling empty files or files with no data rows.

def test_read_csv_empty_file_raises(tmp_path):
    f = make_csv(tmp_path, "empty.csv", "")
    with pytest.raises(ValueError, match="no headers"):
        list(read_csv(f))

def test_read_csv_headers_only_returns_empty_list(tmp_path):
    f = make_csv(tmp_path, "headers.csv", "name,age\n")
    rows = list(read_csv(f))
    assert rows == []


# Tests for various error conditions during reading.

def test_read_csv_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        list(read_csv(tmp_path / "missing.csv"))

def test_read_csv_wrong_extension_raises(tmp_path):
    f = tmp_path / "data.txt"
    f.write_text("name,age\nAlice,30\n")
    with pytest.raises(ValueError, match=".txt"):
        list(read_csv(f))


# Tests for the get_headers functionality.

def test_get_headers_returns_correct_list(tmp_path):
    f = make_csv(tmp_path, "data.csv", "name,age,city\nAlice,30,Dhaka\n")
    headers = get_headers(f)
    assert headers == ["name", "age", "city"]

def test_get_headers_strips_whitespace(tmp_path):
    f = make_csv(tmp_path, "data.csv", " name , age \nAlice,30\n")
    headers = get_headers(f)
    assert headers == ["name", "age"]