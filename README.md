# logslice

A CLI tool to filter and slice structured log files by time range or field value.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Filter logs by time range
logslice --file app.log --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00"

# Filter by field value
logslice --file app.log --field level --value ERROR

# Combine filters and output to file
logslice --file app.log --start "2024-01-15T08:00:00" --field service --value auth -o filtered.log
```

**Supported formats:** JSON Lines (`.jsonl`), newline-delimited JSON logs.

### Options

| Flag | Description |
|------|-------------|
| `--file` | Path to the log file |
| `--start` | Start timestamp (ISO 8601) |
| `--end` | End timestamp (ISO 8601) |
| `--field` | Field name to filter on |
| `--value` | Value to match for the given field |
| `-o` | Output file (defaults to stdout) |

---

## Requirements

- Python 3.8+

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).