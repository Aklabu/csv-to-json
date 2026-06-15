from pathlib import Path
from dataclasses import dataclass, field


# holds the outcome of a validation run
@dataclass
class ValidationResult:
    valid: bool = True
    errors: list[str] = field(default_factory=list)

    # mark as invalid and record the error message
    def fail(self, msg: str):
        self.valid = False
        self.errors.append(msg)

    def __str__(self):
        if self.valid:
            return "Validation passed."
        return "Validation failed:\n" + "\n".join(f"  - {e}" for e in self.errors)


"""
Validate CSV data by ensuring required columns exist, specified columns contain
unique values, and designated fields are not null or empty.
"""
def validate(
    rows: list[dict],
    required_columns: list[str] = None,
    unique_columns: list[str] = None,
    not_null_columns: list[str] = None,
) -> ValidationResult:
    result = ValidationResult()

    if not rows:
        result.fail("No data rows found.")
        return result

    headers = set(rows[0].keys())

    # check that all required columns exist in the headers
    for col in (required_columns or []):
        if col not in headers:
            result.fail(f"Required column missing: '{col}'")

    # check for None or empty values in not-null columns
    # row index starts at 2 because row 1 is the header
    for col in (not_null_columns or []):
        if col not in headers:
            continue
        for i, row in enumerate(rows, start=2):
            if row.get(col) in (None, ""):
                result.fail(f"Null value in column '{col}' at row {i}")

    # check for duplicate values in unique columns
    for col in (unique_columns or []):
        if col not in headers:
            continue
        seen = {}
        for i, row in enumerate(rows, start=2):
            val = row.get(col)
            if val in seen:
                result.fail(
                    f"Duplicate value '{val}' in column '{col}' "
                    f"at rows {seen[val]} and {i}"
                )
            else:
                seen[val] = i

    return result