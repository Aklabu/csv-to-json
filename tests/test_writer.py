import json
import pytest
from pathlib import Path
from converter.writer import write_json, write_json_stream


# Helper functions for testing JSON writing.

# Reads and parses a JSON file from the disk.
def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# Tests for standard JSON writing functionality.

def test_write_json_creates_file(tmp_path):
    data = [{"name": "Alice", "age": 30}]
    out = tmp_path / "out.json"
    write_json(data, out)
    assert out.exists()

def test_write_json_content_is_correct(tmp_path):
    data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    out = tmp_path / "out.json"
    write_json(data, out)
    result = load_json(out)
    assert result == data

def test_write_json_with_dict_data(tmp_path):
    data = {"Engineering": [{"name": "Alice"}], "Marketing": [{"name": "Bob"}]}
    out = tmp_path / "grouped.json"
    write_json(data, out)
    result = load_json(out)
    assert result == data

# Ensure the output directory is created automatically if missing.
def test_write_json_creates_parent_dirs(tmp_path):
    out = tmp_path / "nested" / "folder" / "out.json"
    write_json([{"x": 1}], out)
    assert out.exists()

def test_write_json_respects_indent(tmp_path):
    data = [{"name": "Alice"}]
    out = tmp_path / "out.json"
    write_json(data, out, indent=2)
    raw = out.read_text()
    # Verify that lines start with 2 spaces due to indent parameter.
    assert "  " in raw

def test_write_json_empty_list(tmp_path):
    out = tmp_path / "out.json"
    write_json([], out)
    result = load_json(out)
    assert result == []

# Ensure non-serializable types use string fallback instead of failing.
def test_write_json_non_serialisable_uses_str_fallback(tmp_path):
    data = [{"tags": {1, 2, 3}}]  # Include a set to test fallback behavior.
    out = tmp_path / "out.json"
    write_json(data, out)  # This should complete without exceptions.
    assert out.exists()


# Tests for streaming JSON writing functionality.

def test_write_json_stream_creates_file(tmp_path):
    rows = [{"name": "Alice"}, {"name": "Bob"}]
    out = tmp_path / "stream.json"
    write_json_stream(iter(rows), out)
    assert out.exists()

def test_write_json_stream_content_is_correct(tmp_path):
    rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    out = tmp_path / "stream.json"
    write_json_stream(iter(rows), out)
    result = load_json(out)
    assert result == rows

def test_write_json_stream_returns_row_count(tmp_path):
    rows = [{"x": i} for i in range(5)]
    out = tmp_path / "stream.json"
    count = write_json_stream(iter(rows), out)
    assert count == 5

# Ensure streamed output forms valid JSON without trailing commas.
def test_write_json_stream_valid_json_no_trailing_comma(tmp_path):
    rows = [{"a": 1}, {"b": 2}, {"c": 3}]
    out = tmp_path / "stream.json"
    write_json_stream(iter(rows), out)
    raw = out.read_text()
    # The last element must not end with a comma before the closing bracket.
    assert not raw.strip().endswith(",]")
    load_json(out)  # The generated JSON must parse without throwing errors.

def test_write_json_stream_empty_iterator(tmp_path):
    out = tmp_path / "empty_stream.json"
    count = write_json_stream(iter([]), out)
    result = load_json(out)
    assert result == []
    assert count == 0

# Ensure parent directories are generated automatically during streaming.
def test_write_json_stream_creates_parent_dirs(tmp_path):
    out = tmp_path / "deep" / "dir" / "stream.json"
    write_json_stream(iter([{"x": 1}]), out)
    assert out.exists()