import csv
import glob
import os
import re
from datetime import datetime

TRADEMARKS_RE = re.compile(r"[\u2122\u00AE\u00A9]")  # ™ ® ©
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def detect_delimiter(path):
    with open(path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        sample = f.read(65536)
        f.seek(0)
        try:
            d = csv.Sniffer().sniff(sample, delimiters=[',',';','\t'])
            return d.delimiter
        except Exception:
            return ';' if sample.count(';') > sample.count(',') else ','


def norm_title_strong(s: str) -> str:
    if not s:
        return ''
    s = s.lower()
    s = TRADEMARKS_RE.sub('', s)
    s = s.replace('&', ' and ')
    # keep the main title before common separators
    for sep in [' - ', ' — ', ' : ', ' | ']:
        if sep in s:
            s = s.split(sep)[0]
    # remove non-alphanumeric, collapse spaces
    s = NON_ALNUM_RE.sub(' ', s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def find_latest_combined():
    files = sorted(glob.glob('COMBINED_apps_*_excel.csv'), key=os.path.getmtime, reverse=True)
    if files:
        return files[0]
    # fallback to schema semicolon CSV if excel not present
    files = sorted([f for f in glob.glob('COMBINED_apps_*.csv') if not f.endswith('_simple.csv')], key=os.path.getmtime, reverse=True)
    return files[0] if files else None


def export_duplicates(mode: str = 'strong') -> str:
    path = find_latest_combined()
    if not path:
        raise FileNotFoundError('No combined CSV files found.')
    delim = detect_delimiter(path)

    # Read rows with normalized headers
    with open(path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = reader.fieldnames or []
        def _norm_header(h):
            if not isinstance(h, str):
                return h
            return h.replace('\ufeff', '').strip()
        norm_fieldnames = [_norm_header(h) for h in fieldnames]
        rows_raw = list(reader)
    rows = []
    for r in rows_raw:
        nr = {}
        for k, v in r.items():
            nk = k.replace('\ufeff', '').strip() if isinstance(k, str) else k
            nr[nk] = v
        rows.append(nr)

    # Group by title normalization
    groups = {}
    for r in rows:
        title = r.get('App_Name') or ''
        key = title.strip().lower() if mode == 'exact' else norm_title_strong(title)
        groups.setdefault(key, []).append(r)

    # Prepare output
    ts = datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%fZ')[:-3] + 'Z'
    out_path = f"DUPLICATE_TITLES_{mode}_{ts}.csv"
    out_cols = [
        'dup_key', 'dup_count', 'App_Name', 'developer', 'store',
        'appId_appStore', 'appId_playStore', 'score_appStore', 'score_playStore',
        'reviews_appStore', 'reviews_playStore', 'url'
    ]

    dup_total_rows = 0
    dup_groups = 0

    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=out_cols, delimiter=';')
        w.writeheader()
        # deterministic ordering: sort groups by key, then rows by store/developer/name
        def store_rank(s: str) -> int:
            s = (s or '').lower()
            if s == 'both':
                return 0
            if 'apple' in s:
                return 1
            if 'google' in s:
                return 2
            return 3
        for k in sorted(groups.keys()):
            lst = groups[k]
            if k and len(lst) > 1:
                dup_groups += 1
                dup_total_rows += len(lst)
                lst_sorted = sorted(
                    lst,
                    key=lambda r: (
                        store_rank(r.get('store')), (r.get('developer') or '').lower(), (r.get('App_Name') or '').lower()
                    ),
                )
                for r in lst_sorted:
                    w.writerow({
                        'dup_key': k,
                        'dup_count': len(lst),
                        'App_Name': r.get('App_Name', ''),
                        'developer': r.get('developer', ''),
                        'store': r.get('store', ''),
                        'appId_appStore': r.get('appId_appStore', ''),
                        'appId_playStore': r.get('appId_playStore', ''),
                        'score_appStore': r.get('score_appStore', ''),
                        'score_playStore': r.get('score_playStore', ''),
                        'reviews_appStore': r.get('reviews_appStore', ''),
                        'reviews_playStore': r.get('reviews_playStore', ''),
                        'url': r.get('url', ''),
                    })

    print(f"Wrote {out_path} with {dup_groups} duplicate title groups and {dup_total_rows} rows.")
    return out_path


if __name__ == '__main__':
    export_duplicates('strong')
