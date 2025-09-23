import csv
import glob
import os
from collections import Counter

def detect_delimiter(path):
    with open(path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        sample = f.read(65536)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[',',';','\t'])
            return dialect.delimiter
        except Exception:
            return ';' if sample.count(';') > sample.count(',') else ','


def validate(path, expected_cols=None, delimiter=None, max_check=200000):
    if delimiter is None:
        delimiter = detect_delimiter(path)
    print(f"Validating: {os.path.basename(path)} (delimiter '{delimiter}')")

    counts = Counter()
    newline_rows = 0
    total = 0

    with open(path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        reader = csv.reader(f, delimiter=delimiter)
        header = next(reader)
        expected = expected_cols or len(header)
        print(f"Header columns: {len(header)}")
        # quick peek at first 10 headers
        print(f"First 10 columns: {header[:10]}")
        for row in reader:
            total += 1
            if total > max_check:
                break
            counts[len(row)] += 1
            # check for embedded newlines (unlikely if parsed correctly, but verify)
            for cell in row:
                if '\n' in str(cell) or '\r' in str(cell):
                    newline_rows += 1
                    break

    print(f"Rows checked: {total}")
    print(f"Column count distribution (row_count -> occurrences):")
    for k in sorted(counts.keys()):
        print(f"  {k}: {counts[k]}")
    print(f"Rows with embedded newlines: {newline_rows}")
    if expected:
        bad = sum(v for k,v in counts.items() if k != expected)
        print(f"Rows not matching expected column count ({expected}): {bad}")
    return {
        'total': total,
        'header_cols': len(header),
        'counts': counts,
        'newline_rows': newline_rows
    }

if __name__ == '__main__':
    # Prefer most recent combined outputs
    files = sorted(glob.glob('COMBINED_apps_*.*'), key=os.path.getmtime, reverse=True)
    targets = []
    for f in files:
        if f.endswith('_simple.csv') or f.endswith('.csv'):
            targets.append(f)
        if len(targets) >= 2:
            break
    if not targets:
        print("No COMBINED_apps outputs found.")
    else:
        for t in targets:
            print("\n---")
            validate(t)
