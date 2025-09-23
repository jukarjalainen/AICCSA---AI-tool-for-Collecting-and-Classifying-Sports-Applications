import csv
import os
import re


def detect_delimiter(path):
    with open(path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        sample = f.read(65536)
        f.seek(0)
        try:
            d = csv.Sniffer().sniff(sample, delimiters=[',',';','\t'])
            return d.delimiter
        except Exception:
            return ';' if sample.count(';') > sample.count(',') else ','


def norm_text(s: str) -> str:
    if not s:
        return ''
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def count_both_scores(combined_csv: str):
    delim = detect_delimiter(combined_csv)
    both = 0
    total = 0
    with open(combined_csv, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        rdr = csv.DictReader(f, delimiter=delim)
        for row in rdr:
            total += 1
            if (row.get('score_appStore') or '').strip() and (row.get('score_playStore') or '').strip():
                both += 1
    print(f"Rows with both scores: {both} / {total}")


def key_intersection(appstore_csv: str, playstore_csv: str):
    d1 = detect_delimiter(appstore_csv)
    d2 = detect_delimiter(playstore_csv)
    ks1 = set()
    ks2 = set()
    with open(appstore_csv, 'r', encoding='utf-8', errors='ignore', newline='') as f1:
        r1 = csv.DictReader(f1, delimiter=d1)
        for r in r1:
            ks1.add((norm_text(r.get('title')), norm_text(r.get('developer'))))
    with open(playstore_csv, 'r', encoding='utf-8', errors='ignore', newline='') as f2:
        r2 = csv.DictReader(f2, delimiter=d2)
        for r in r2:
            ks2.add((norm_text(r.get('title')), norm_text(r.get('developer'))))
    inter = ks1 & ks2
    print(f"Title+Developer exact normalized matches: {len(inter)} (AppStore set: {len(ks1)}, PlayStore set: {len(ks2)})")


if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    # pick latest _excel.csv if present
    candidates = [p for p in os.listdir(base) if p.startswith('COMBINED_apps_') and p.endswith('_excel.csv')]
    combined = None
    if candidates:
        combined = max([os.path.join(base, p) for p in candidates], key=os.path.getmtime)
    if combined:
        count_both_scores(combined)
    else:
        print('No combined _excel.csv found in this folder.')
    appstore_path = os.path.join(base, 'AppStoreAppsCSV.csv')
    playstore_path = os.path.join(base, 'PlayStoreAppsCSV.csv')
    if os.path.exists(appstore_path) and os.path.exists(playstore_path):
        key_intersection(appstore_path, playstore_path)
    else:
        print('Source CSVs not found for key intersection check.')
