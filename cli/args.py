import argparse


# build and return the argument parser with all supported flags
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv_to_json",
        description="Convert CSV files to JSON with type inference, validation, grouping, and batch support.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # positional argument 

    # input can be a single .csv file or a folder (used with --batch)
    p.add_argument(
        "input",
        help="Path to a .csv file OR a folder (use with --batch)",
    )

    # output 

    # custom output path; defaults to same location as input with .json extension
    p.add_argument(
        "-o", "--output",
        metavar="PATH",
        help="Output .json file or folder path\n(default: same location as input)",
    )

    # JSON indentation level
    p.add_argument(
        "--indent",
        type=int,
        default=4,
        metavar="N",
        help="JSON indentation level (default: 4)",
    )

    # type inference

    # auto-cast values to int, float, bool, date, or None
    p.add_argument(
        "--infer-types",
        action="store_true",
        help="Auto-cast values to int, float, bool, date, or None",
    )

    # streaming 

    # stream output row by row to avoid loading large files into memory
    p.add_argument(
        "--stream",
        action="store_true",
        help="Stream output for large files (avoids loading all rows into memory)",
    )

    # grouping

    # group rows by a single column value
    p.add_argument(
        "--group-by",
        metavar="COLUMN",
        help="Group rows by a column value to produce nested JSON\ne.g. --group-by department",
    )

    # group rows by multiple columns recursively
    p.add_argument(
        "--group-by-multi",
        metavar="COL",
        nargs="+",
        help="Recursively group rows by multiple columns\ne.g. --group-by-multi department role",
    )

    # batch mode

    # convert all CSV files in a folder at once
    p.add_argument(
        "--batch",
        action="store_true",
        help="Convert all CSV files in the input folder",
    )

    # also search sub-folders when running in batch mode
    p.add_argument(
        "--recursive",
        action="store_true",
        help="(with --batch) also search sub-folders for CSV files",
    )

    # validation 

    # run validation checks before writing output
    p.add_argument(
        "--validate",
        action="store_true",
        help="Run validation checks before writing output",
    )

    # columns that must exist in the CSV headers
    p.add_argument(
        "--require",
        metavar="COL",
        nargs="+",
        help="(with --validate) columns that must exist\ne.g. --require name email",
    )

    # columns that must not contain empty or None values
    p.add_argument(
        "--not-null",
        metavar="COL",
        nargs="+",
        help="(with --validate) columns that must not be empty\ne.g. --not-null id email",
    )

    # columns whose values must be unique across all rows
    p.add_argument(
        "--unique",
        metavar="COL",
        nargs="+",
        help="(with --validate) columns whose values must be unique\ne.g. --unique id email",
    )

    # encoding 

    # force a specific file encoding instead of auto-detecting
    p.add_argument(
        "--encoding",
        metavar="ENC",
        help="Force a specific file encoding\ne.g. --encoding latin-1",
    )

    return p


# parse command-line arguments and return the Namespace object
def parse_args() -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args()
    _validate_args(args, parser)
    return args


# cross-flag validation — catch invalid combinations before running
def _validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:

    # recursive only makes sense with --batch
    if args.recursive and not args.batch:
        parser.error("--recursive requires --batch")

    # require, not-null, unique only make sense with validate
    if (args.require or args.not_null or args.unique) and not args.validate:
        parser.error("--require / --not-null / --unique require --validate")

    # group-by and group-by-multi are mutually exclusive
    if args.group_by and args.group_by_multi:
        parser.error("--group-by and --group-by-multi cannot be used together")

    # stream with group-by is not supported (grouping requires all rows in memory)
    if args.stream and args.group_by:
        parser.error("--stream cannot be used with --group-by (grouping requires all rows in memory)")

    # stream with group-by-multi is not supported for the same reason
    if args.stream and args.group_by_multi:
        parser.error("--stream cannot be used with --group-by-multi")