# converter/batch.py

from pathlib import Path
from dataclasses import dataclass, field

from converter.reader import read_csv
from converter.writer import write_json, write_json_stream
from converter.type_inference import infer_row
from converter.grouper import group_by


# tracks which files succeeded and which failed during a batch run
@dataclass
class BatchResult:
    succeeded: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)  # filename -> error message

    @property
    def total(self): return len(self.succeeded) + len(self.failed)

    # return a human-readable summary of the batch run
    def summary(self) -> str:
        lines = [
            f"\n Batch Summary",
            f"   Total   : {self.total}",
            f"   OK   : {len(self.succeeded)}",
            f"   Failed: {len(self.failed)}",
        ]
        if self.failed:
            lines.append("\n   Failures:")
            for name, err in self.failed.items():
                lines.append(f"     • {name}: {err}")
        return "\n".join(lines)


# convert all CSV files in a folder to JSON
# input_dir  - folder containing CSV files
# output_dir - where to save JSON files, defaults to same as input_dir
# infer_types - auto-cast values to Python types
# stream     - use streaming writer to avoid loading large files into memory
# group_key  - column name to group rows by, produces nested JSON
# indent     - JSON indentation level
# recursive  - if True, also search sub-folders for CSV files
def convert_folder(
    input_dir: str | Path,
    output_dir: str | Path = None,
    infer_types: bool = False,
    stream: bool = False,
    group_key: str = None,
    indent: int = 4,
    recursive: bool = False,
) -> BatchResult:
    input_dir  = Path(input_dir)
    output_dir = Path(output_dir) if output_dir else input_dir

    if not input_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {input_dir}")

    # use recursive glob pattern if --recursive flag is set
    glob = "**/*.csv" if recursive else "*.csv"
    csv_files = sorted(input_dir.glob(glob))

    if not csv_files:
        print(f"⚠️  No CSV files found in: {input_dir}")
        return BatchResult()

    result = BatchResult()

    for csv_path in csv_files:
        # mirror sub-folder structure from input_dir into output_dir
        relative = csv_path.relative_to(input_dir)
        out_path  = output_dir / relative.with_suffix(".json")

        print(f"\n🔄 Processing: {csv_path.name}")
        try:
            if stream and not group_key:
                # stream rows directly to disk without loading all into memory
                rows_iter = read_csv(csv_path, infer_types=infer_types)
                write_json_stream(rows_iter, out_path, indent=indent)
            else:
                rows = list(read_csv(csv_path, infer_types=infer_types))
                data = group_by(rows, group_key) if group_key else rows
                write_json(data, out_path, indent=indent)

            result.succeeded.append(csv_path.name)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            result.failed[csv_path.name] = str(e)

    print(result.summary())
    return result