import csv
import glob
import os
from datetime import datetime
import re

def find_latest_combined():
    # Search in current folder and workspace root (one level up)
    candidates = []
    for base in ['.', '..']:
        candidates.extend(glob.glob(os.path.join(base, 'COMBINED_apps_*.csv')))
    # Prefer the semicolon schema version over _simple.csv and skip already _excel.csv
    candidates = [f for f in candidates if not f.endswith('_excel.csv')]
    candidates.sort(key=os.path.getmtime, reverse=True)
    for f in candidates:
        if not f.endswith('_simple.csv'):
            return f
    return candidates[0] if candidates else None


_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\u2028\u2029]")


def clean_cell(s: str) -> str:
    if s is None:
        return ''
    s = str(s)
    # Replace newlines and carriage returns with spaces
    s = s.replace('\r', ' ').replace('\n', ' ')
    # Remove other control characters (including Unicode LS/PS) that can confuse Excel/Power Query
    s = _CONTROL_CHARS_RE.sub(' ', s)
    # Collapse multiple spaces
    while '  ' in s:
        s = s.replace('  ', ' ')
    return s.strip()


def make_excel_friendly(input_csv: str) -> str:
    # Read with correct delimiter (semicolon for schema CSV)
    with open(input_csv, 'r', encoding='utf-8', errors='ignore', newline='') as f_in:
        reader = csv.reader(f_in, delimiter=';')
        header = next(reader)
        rows = []
        for row in reader:
            rows.append([clean_cell(c) for c in row])

    ts = datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%fZ')[:-3] + 'Z'
    out_csv = input_csv.replace('.csv', f'_excel.csv')

    # Write with semicolon delimiter and quote all to help Excel/Power Query
    with open(out_csv, 'w', encoding='utf-8', newline='') as f_out:
        writer = csv.writer(f_out, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(rows)

    return out_csv

if __name__ == '__main__':
    latest = find_latest_combined()
    if not latest:
        print('No COMBINED_apps CSVs found.')
    else:
        out = make_excel_friendly(latest)
        print(f'Excel-friendly file written: {out}')
