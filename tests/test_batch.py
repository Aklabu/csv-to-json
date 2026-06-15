import json
import pytest
from pathlib import Path
from converter.batch import convert_folder, BatchResult


# Helper functions for testing batch conversion.

# Writes a CSV file inside the specified folder.
def make_csv(folder: Path, filename: str, content: str) -> Path:
    p = folder / filename
    p.write_text(content, encoding="utf-8")
    return p

# Reads and parses a JSON file from disk.
def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# Tests for basic batch conversion functionality.

def test_batch_converts_single_file(tmp_path):
    make_csv(tmp_path, "a.csv", "name,age\nAlice,30\n")
    result = convert_folder(tmp_path)
    assert "a.csv" in result.succeeded
    assert (tmp_path / "a.json").exists()

def test_batch_converts_multiple_files(tmp_path):
    make_csv(tmp_path, "a.csv", "name,age\nAlice,30\n")
    make_csv(tmp_path, "b.csv", "city,pop\nDhaka,10000000\n")
    result = convert_folder(tmp_path)
    assert len(result.succeeded) == 2
    assert (tmp_path / "a.json").exists()
    assert (tmp_path / "b.json").exists()

def test_batch_json_content_is_correct(tmp_path):
    make_csv(tmp_path, "data.csv", "name,age\nAlice,30\n")
    convert_folder(tmp_path)
    data = load_json(tmp_path / "data.json")
    assert data == [{"name": "Alice", "age": "30"}]

def test_batch_with_infer_types(tmp_path):
    make_csv(tmp_path, "data.csv", "name,age\nAlice,30\n")
    convert_folder(tmp_path, infer_types=True)
    data = load_json(tmp_path / "data.json")
    assert data[0]["age"] == 30  # Age should be cast to integer.


# Tests for custom output directory functionality.

def test_batch_saves_to_custom_output_dir(tmp_path):
    input_dir  = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    make_csv(input_dir, "data.csv", "name,age\nAlice,30\n")
    convert_folder(input_dir, output_dir=output_dir)
    assert (output_dir / "data.json").exists()

# Output directory is created automatically if it does not exist.
def test_batch_creates_output_dir_if_missing(tmp_path):
    out = tmp_path / "new_output"
    make_csv(tmp_path, "data.csv", "name,age\nAlice,30\n")
    convert_folder(tmp_path, output_dir=out)
    assert out.exists()


# Tests for recursive mode during batch conversion.

def test_batch_recursive_finds_nested_csvs(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    make_csv(tmp_path, "root.csv", "name,age\nAlice,30\n")
    make_csv(sub, "nested.csv", "city,pop\nDhaka,10000000\n")
    result = convert_folder(tmp_path, recursive=True)
    assert len(result.succeeded) == 2

def test_batch_non_recursive_ignores_nested_csvs(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    make_csv(tmp_path, "root.csv", "name,age\nAlice,30\n")
    make_csv(sub, "nested.csv", "city,pop\nDhaka,10000000\n")
    result = convert_folder(tmp_path, recursive=False)
    assert len(result.succeeded) == 1


# Tests for streaming mode during batch conversion.

def test_batch_stream_mode_produces_valid_json(tmp_path):
    make_csv(tmp_path, "data.csv", "name,age\nAlice,30\nBob,25\n")
    convert_folder(tmp_path, stream=True)
    data = load_json(tmp_path / "data.json")
    assert len(data) == 2


# Tests for grouping functionality during batch conversion.

def test_batch_group_by_produces_nested_json(tmp_path):
    content = "name,dept\nAlice,Engineering\nBob,Marketing\nCarol,Engineering\n"
    make_csv(tmp_path, "data.csv", content)
    convert_folder(tmp_path, group_key="dept")
    data = load_json(tmp_path / "data.json")
    assert "Engineering" in data
    assert "Marketing" in data
    assert len(data["Engineering"]) == 2


# Tests for error handling during batch conversion.

def test_batch_invalid_directory_raises(tmp_path):
    with pytest.raises(NotADirectoryError):
        convert_folder(tmp_path / "nonexistent")

def test_batch_empty_folder_returns_empty_result(tmp_path):
    result = convert_folder(tmp_path)
    assert result.total == 0

def test_batch_failed_file_recorded_in_result(tmp_path):
    # Write a CSV with no headers to force a read error.
    bad = tmp_path / "bad.csv"
    bad.write_text("", encoding="utf-8")
    result = convert_folder(tmp_path)
    assert "bad.csv" in result.failed


# Tests for the BatchResult class.

def test_batch_result_total_count(tmp_path):
    make_csv(tmp_path, "a.csv", "name,age\nAlice,30\n")
    make_csv(tmp_path, "b.csv", "name,age\nBob,25\n")
    result = convert_folder(tmp_path)
    assert result.total == 2

def test_batch_result_summary_contains_counts(tmp_path):
    make_csv(tmp_path, "a.csv", "name,age\nAlice,30\n")
    result = convert_folder(tmp_path)
    summary = result.summary()
    assert "1" in summary  # Summary should show at least one success.