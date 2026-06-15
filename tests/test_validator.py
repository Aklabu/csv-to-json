import pytest
from converter.validator import validate, ValidationResult


# Tests for validating empty data sets.

def test_empty_rows_fails():
    result = validate([])
    assert result.valid is False
    assert any("No data" in e for e in result.errors)


# Tests for validating required columns presence.

def test_required_column_present_passes():
    rows = [{"name": "Alice", "age": 30}]
    result = validate(rows, required_columns=["name"])
    assert result.valid is True

def test_required_column_missing_fails():
    rows = [{"name": "Alice"}]
    result = validate(rows, required_columns=["email"])
    assert result.valid is False
    assert any("email" in e for e in result.errors)

def test_multiple_required_columns_one_missing_fails():
    rows = [{"name": "Alice", "age": 30}]
    result = validate(rows, required_columns=["name", "email"])
    assert result.valid is False
    assert any("email" in e for e in result.errors)


# Tests for validating columns that cannot be null.

def test_not_null_column_with_values_passes():
    rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    result = validate(rows, not_null_columns=["name"])
    assert result.valid is True

def test_not_null_column_with_none_fails():
    rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": None}]
    result = validate(rows, not_null_columns=["name"])
    assert result.valid is False
    assert any("name" in e for e in result.errors)

def test_not_null_column_with_empty_string_fails():
    rows = [{"id": 1, "name": ""}]
    result = validate(rows, not_null_columns=["name"])
    assert result.valid is False

# Ensure non-existent columns in not_null_columns are silently skipped.
def test_not_null_on_missing_column_is_skipped():
    rows = [{"name": "Alice"}]
    result = validate(rows, not_null_columns=["email"])
    assert result.valid is True


# Tests for validating unique constraints on columns.

def test_unique_column_with_distinct_values_passes():
    rows = [{"id": 1}, {"id": 2}, {"id": 3}]
    result = validate(rows, unique_columns=["id"])
    assert result.valid is True

def test_unique_column_with_duplicate_values_fails():
    rows = [{"id": 1}, {"id": 2}, {"id": 1}]
    result = validate(rows, unique_columns=["id"])
    assert result.valid is False
    assert any("id" in e for e in result.errors)

# Ensure non-existent columns in unique_columns are silently skipped.
def test_unique_on_missing_column_is_skipped():
    rows = [{"name": "Alice"}]
    result = validate(rows, unique_columns=["email"])
    assert result.valid is True


# Tests for applying multiple validation rules simultaneously.

def test_all_rules_pass_together():
    rows = [
        {"id": 1, "name": "Alice", "email": "a@x.com"},
        {"id": 2, "name": "Bob",   "email": "b@x.com"},
    ]
    result = validate(
        rows,
        required_columns=["id", "name", "email"],
        not_null_columns=["name"],
        unique_columns=["id", "email"],
    )
    assert result.valid is True

def test_multiple_rules_multiple_failures():
    rows = [{"id": 1, "name": ""}, {"id": 1, "name": "Bob"}]
    result = validate(
        rows,
        required_columns=["email"],  # Expect validation failure due to missing column.
        not_null_columns=["name"],  # Expect validation failure due to empty value.
        unique_columns=["id"],  # Expect validation failure due to duplicate id.
    )
    assert result.valid is False
    assert len(result.errors) == 3


# Tests for the ValidationResult class methods.

def test_validation_result_str_on_pass():
    v = ValidationResult()
    assert "passed" in str(v)

def test_validation_result_str_on_fail():
    v = ValidationResult()
    v.fail("something went wrong")
    assert "failed" in str(v)
    assert "something went wrong" in str(v)