import sys
from pathlib import Path

from cli.args import parse_args
from converter.reader import read_csv
from converter.writer import write_json, write_json_stream
from converter.validator import validate
from converter.grouper import group_by, group_by_multi
from converter.batch import convert_folder


# handle a single CSV file conversion
def run(args) -> int:

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

    print(f"Input  : {input_path}")
    print(f"Output : {out_path}")

    # read rows from the CSV file
    rows = list(read_csv(input_path, infer_types=args.infer_types, encoding=args.encoding))
    print(f"   Rows read: {len(rows)}")

    if not rows:
        print("No data rows found. Exiting.")
        return 1

    # run validation if --validate flag is set
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

    # apply grouping if requested
    if args.group_by_multi:
        data = group_by_multi(rows, args.group_by_multi)
    elif args.group_by:
        data = group_by(rows, args.group_by)
    else:
        data = rows

    # write output using stream or normal writer
    if args.stream and isinstance(data, list):
        write_json_stream(iter(data), out_path, indent=args.indent)
    else:
        write_json(data, out_path, indent=args.indent)

    print("Done!")
    return 0


def main():
    # parse and cross-validate all CLI flags
    args = parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()