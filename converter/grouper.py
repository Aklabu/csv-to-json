from collections import defaultdict

"""
Group rows by a specified column, returning a nested dictionary keyed by the
column's values. Raises KeyError if the column does not exist.
"""
def group_by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    if not rows:
        return {}

    if key not in rows[0]:
        available = ", ".join(rows[0].keys())
        raise KeyError(
            f"Group-by column '{key}' not found. "
            f"Available columns: {available}"
        )

    grouped: dict[str, list] = defaultdict(list)
    for row in rows:
        # use "__empty__" as fallback key for blank values
        group_val = str(row.get(key, "")).strip() or "__empty__"
        grouped[group_val].append(row)

    return dict(grouped)


# recursively group rows by multiple keys to produce deeply nested JSON
# keys=["department", "role"] produces:
# { "Engineering": { "Senior": [...], "Junior": [...] }, "Marketing": { ... } }
def group_by_multi(rows: list[dict], keys: list[str]) -> dict:
    if not keys or not rows:
        return rows

    top_key = keys[0]
    remaining = keys[1:]
    first_level = group_by(rows, top_key)

    # recurse into each group with the remaining keys
    return {
        group: group_by_multi(group_rows, remaining)
        for group, group_rows in first_level.items()
    }