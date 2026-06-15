import pytest
from converter.type_inference import infer_type, infer_row


# Tests for type inference of None or empty string values.

def test_empty_string_returns_none():
    assert infer_type("") is None

def test_whitespace_returns_none():
    assert infer_type("   ") is None

def test_null_string_returns_none():
    assert infer_type("null") is None

def test_none_string_returns_none():
    assert infer_type("none") is None

def test_na_string_returns_none():
    assert infer_type("n/a") is None

def test_dash_returns_none():
    assert infer_type("-") is None


# Tests for type inference of boolean string values.

def test_true_string_returns_true():
    assert infer_type("true") is True

def test_yes_string_returns_true():
    assert infer_type("yes") is True

def test_false_string_returns_false():
    assert infer_type("false") is False

def test_no_string_returns_false():
    assert infer_type("no") is False

# Ensure boolean inference is case-insensitive.
def test_true_uppercase_returns_true():
    assert infer_type("TRUE") is True

def test_false_mixed_case_returns_false():
    assert infer_type("False") is False


# Tests for type inference of integer string values.

def test_positive_integer():
    assert infer_type("42") == 42

def test_negative_integer():
    assert infer_type("-7") == -7

def test_zero_integer():
    assert infer_type("0") == 0


# Tests for type inference of float string values.

def test_positive_float():
    assert infer_type("3.14") == 3.14

def test_negative_float():
    assert infer_type("-0.5") == -0.5

# Commas in numeric strings should be stripped before parsing.
def test_float_with_comma_separator():
    assert infer_type("1,000.5") == 1000.5


# Tests for type inference of various date string formats.

def test_iso_date_format():
    assert infer_type("2024-01-15") == "2024-01-15"

def test_dmy_slash_date_format():
    assert infer_type("15/01/2024") == "2024-01-15"

def test_mdy_slash_date_format():
    assert infer_type("01/15/2024") == "2024-01-15"

def test_dmy_dash_date_format():
    assert infer_type("15-01-2024") == "2024-01-15"


# Tests for values that should fall back to plain strings.

def test_plain_string_returned_as_is():
    assert infer_type("Dhaka") == "Dhaka"

def test_mixed_alphanumeric_returned_as_string():
    assert infer_type("ABC123") == "ABC123"


# Tests for non-string inputs being processed properly.

# Ensure infer_type returns non-string values completely unchanged.
def test_integer_input_returned_unchanged():
    assert infer_type(99) == 99

def test_none_input_returned_unchanged():
    assert infer_type(None) is None


# Tests for row-level type inference.

def test_infer_row_casts_all_values():
    row = {"name": "Alice", "age": "30", "active": "true", "score": "9.5"}
    result = infer_row(row)
    assert result == {"name": "Alice", "age": 30, "active": True, "score": 9.5}

def test_infer_row_handles_empty_values():
    row = {"name": "Bob", "age": "", "city": "null"}
    result = infer_row(row)
    assert result["age"] is None
    assert result["city"] is None