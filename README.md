# CSV to JSON Converter

A robust, feature-rich command-line tool to convert CSV files to JSON. Built with Python, it supports automatic type inference, grouping, validation, streaming for large files, and batch processing for multiple files at once.

## Features

- **Standard Conversion**: Convert any CSV file to JSON.
- **Type Inference**: Automatically detect and cast integers, floats, booleans, and nulls (`--infer-types`).
- **Grouping**: Produce nested JSON structures by grouping rows by single (`--group-by`) or multiple columns (`--group-by-multi`).
- **Streaming**: Handle large CSV files row-by-row without loading the entire file into memory (`--stream`).
- **Validation**: Enforce schema rules before conversion (`--validate`), checking for required, non-null, and unique columns.
- **Batch Processing**: Convert entire directories of CSVs into JSONs (`--batch`), optionally with subdirectories (`--recursive`).
- **Encoding Management**: Automatically detects encoding but allows forcing a specific one (e.g., `--encoding latin-1`).

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd csv_to_json
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The main entry point for the application is `main.py`. Here are some common examples:

### Basic Conversion
```bash
python main.py sample.csv
```
This will generate `sample.json` in the same directory. To specify an output file:
```bash
python main.py sample.csv -o output.json
```

### Type Inference
Automatically convert numeric and boolean strings to native JSON types:
```bash
python main.py sample.csv --infer-types
```

### Grouping Output
Group rows into nested JSON based on a specific column (e.g., by Location):
```bash
python main.py sample.csv --group-by Location
```
Or recursively group by multiple columns:
```bash
python main.py sample.csv --group-by-multi Location Age
```

### Stream Large Files
If you have a massive CSV, stream it to avoid memory issues (Note: streaming cannot be used with grouping):
```bash
python main.py sample.csv --stream
```

### Data Validation
Ensure the CSV meets specific criteria before writing the output:
```bash
python main.py sample.csv --validate --require Name Age --not-null Name --unique Name
```

### Batch Processing
Convert all `.csv` files inside a directory to `.json`:
```bash
python main.py ./my_csv_folder/ --batch
```
Include subdirectories:
```bash
python main.py ./my_csv_folder/ --batch --recursive
```

### Formatting
Change the JSON indentation (default is 4):
```bash
python main.py sample.csv --indent 2
```

### Help
To see all available CLI options:
```bash
python main.py --help
```

## Testing

This project uses `pytest` for unit testing. The test suite covers batch processing, readers, writers, type inference, and validation logic.

To run the tests:
```bash
pytest
```
