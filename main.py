import argparse
import sys
from pathlib import Path

from converter.reader import read_csv
from converter.writer import write_json, write_json_stream
from converter.validator import validate
from converter.grouper import group_by, group_by_multi
from converter.batch import convert_folder


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv_to_json",
        description="Convert CSV files to JSON with type inference, validation, grouping, and batch support.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    p.add_argument("input", help="Path to a .csv file OR a folder (use with --batch)")

    p.add_argument("-o", "--output",
        help="Output .json file or folder path (default: same location as input)")

    p.add_argument("--indent", type=int, default=4,
        help="JSON indentation level (default: 4)")

    p.add_argument("--infer-types", action="store_true",
        help="Auto-cast values to int, float, bool, date, or None")

    p.add_argument("--stream", action="store_true",
        help="Stream output for large files (avoids loading all rows into memory)")

    p.add_argument("--group-by", metavar="COLUMN",
        help="Group rows by a column value to produce nested JSON")

    p.add_argument("--group-by-multi", metavar="COL", nargs="+",
        help="Recursively group rows by multiple columns  e.g. --group-by-multi dept role")

    p.add_argument("--batch", action="store_true",
        help="Convert all CSV files in the input folder")

    p.add_argument("--recursive", action="store_true",
        help="(with --batch) also search sub-folders")

    p.add_argument("--validate", action="store_true",
        help="Run validation checks before writing output")

    p.add_argument("--require", metavar="COL", nargs="+",
        help="(with --validate) columns that must exist")

    p.add_argument("--not-null", metavar="COL", nargs="+",
        help="(with --validate) columns that must not be empty")

    p.add_argument("--unique", metavar="COL", nargs="+",
        help="(with --validate) columns whose values must be unique")

    p.add_argument("--encoding",
        help="Force a specific file encoding (e.g. utf-8, latin-1)")

    return p


def run(args: argparse.Namespace) -> int:
    input_path = Path(args.input)

    # Batch mode 
    if args.batch:
        result = convert_folder(
            input_dir   = input_path,
            output_dir  = args.output,
            infer_types = args.infer_types,
            stream      = args.stream,
            group_key   = args.group_by,
            indent      = args.indent,
            recursive   = args.recursive,
        )
        return 0 if not result.failed else 1

    # Single file mode 
    out_path = Path(args.output) if args.output else input_path.with_suffix(".json")

    print(f"\n Input  : {input_path}")
    print(f"Output : {out_path}")

    # Read
    rows = list(read_csv(input_path, infer_types=args.infer_types, encoding=args.encoding))
    print(f"   Rows read: {len(rows)}")

    if not rows:
        print("No data rows found. Exiting.")
        return 1

    # Validate
    if args.validate:
        v = validate(
            rows,
            required_columns = args.require,
            not_null_columns = args.not_null,
            unique_columns   = args.unique,
        )
        print(v)
        if not v.valid:
            return 1

    # Group
    if args.group_by_multi:
        data = group_by_multi(rows, args.group_by_multi)
    elif args.group_by:
        data = group_by(rows, args.group_by)
    else:
        data = rows

    # Write
    if args.stream and isinstance(data, list):
        write_json_stream(iter(data), out_path, indent=args.indent)
    else:
        write_json(data, out_path, indent=args.indent)

    print("Done!")
    return 0


def main():
    parser = build_parser()
    args   = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()