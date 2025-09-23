import csv
import json
import os
import re
from datetime import datetime
import math
import difflib

# Mapping from source columns to AppsSchema columns
APP_STORE_MAPPING = {
    # Map store appId to schema 'id'
    'appId': 'id',
    'title': 'App_Name',
    'url': 'url',
    'description': 'description',
    'descriptionHTML': 'descriptionHTML',
    'summary': 'summary',
    'icon': 'icon',
    'headerImage': 'headerImage',
    'genres': 'genres',
    'genreIds': 'genreIds',
    'primaryGenre': 'primaryGenre',
    'primaryGenreId': 'primaryGenreId',
    'contentRating': 'contentRating',
    'released': 'released',
    'updated': 'updated',
    'version': 'version',
    'price': 'price',
    'currency': 'currency',
    'free': 'free',
    'developer': 'developer',
    'developerId': 'developerId',
    'developerUrl': 'developerUrl',
    'developerWebsite': 'developerWebsite',
    'developerLegalName': 'developerLegalName',
    'privacyPolicy': 'privacyPolicy',
    'score': 'score',
    'reviews': 'reviews',
    'platform': 'platform',
    'platforms': 'platforms',
    'availableOnBothPlatforms': 'availableOnBothPlatforms',
    'sourceMethod': 'sourceMethod',
    'sourceCollection': 'sourceCollection',
    'sourceCountry': 'sourceCountry',
    'searchQuery': 'searchQuery',
    'targetCategory': 'targetCategory',
    'developerInternalID': 'developerInternalID',
}

PLAY_STORE_MAPPING = {
    'title': 'App_Name',
    'description': 'description',
    'descriptionHTML': 'descriptionHTML',
    'summary': 'summary',
    'icon': 'icon',
    'headerImage': 'headerImage',
    'genre': 'genres',
    'genreId': 'genreIds',
    'categories': 'categories',
    'contentRating': 'contentRating',
    'released': 'released',
    'updated': 'updated',
    'version': 'version',
    'price': 'price',
    'currency': 'currency',
    'free': 'free',
    'developer': 'developer',
    'developerId': 'developerId',
    'privacyPolicy': 'privacyPolicy',
    'score': 'score',
    'reviews': 'reviews',
    'ratings': 'ratings',
    'appId': 'id',
    'url': 'url',
    'platform': 'platform',
    'platforms': 'platforms',
    'availableOnBothPlatforms': 'availableOnBothPlatforms',
    'sourceMethod': 'sourceMethod',
    'sourceCollection': 'sourceCollection',
    'sourceCountry': 'sourceCountry',
    'searchQuery': 'searchQuery',
    'targetCategory': 'targetCategory',
    'developerInternalID': 'developerInternalID',
}


def read_schema_columns(schema_path: str):
    with open(schema_path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
    # Use schema exactly as provided
    return header


def read_csv_dicts(path: str):
    # Auto-detect delimiter (comma vs semicolon) with fallback
    with open(path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        sample = f.read(65536)
        f.seek(0)
        delimiter = ','
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[',', ';', '\t'])
            delimiter = dialect.delimiter
        except Exception:
            # Heuristic fallback
            if sample.count(';') > sample.count(','):
                delimiter = ';'
        reader = csv.DictReader(f, delimiter=delimiter)
        rows_raw = list(reader)
        fieldnames = reader.fieldnames or []
        # Normalize headers: strip BOM and surrounding whitespace
        def _norm_header(h):
            if not isinstance(h, str):
                return h
            return h.replace('\ufeff', '').strip()
        norm_fieldnames = [_norm_header(h) for h in fieldnames]
        # If any header changed, rebuild row dicts with normalized keys
        if norm_fieldnames != fieldnames:
            rows = []
            for r in rows_raw:
                nr = {}
                for k, v in r.items():
                    nk = _norm_header(k)
                    nr[nk] = v
                rows.append(nr)
            fieldnames = norm_fieldnames
        else:
            rows = rows_raw
        print(f"Reading {os.path.basename(path)} with delimiter '{delimiter}' and {len(fieldnames)} columns")
        if fieldnames:
            print(f"  First fields: {fieldnames[:10]}")
        return fieldnames, rows


TRADEMARKS_RE = re.compile(r"[\u2122\u00AE\u00A9]")  # ™ ® ©
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def _norm_text(s: str) -> str:
    if s is None:
        return ''
    s = str(s).lower()
    s = TRADEMARKS_RE.sub('', s)
    s = s.replace('&', ' and ')
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _norm_title_for_match(s: str) -> str:
    s = _norm_text(s)
    # keep main title before common separators
    for sep in [' - ', ' — ', ' : ', ' | ']:
        if sep in s:
            s = s.split(sep)[0]
    # remove non-alphanumerics
    s = NON_ALNUM_RE.sub(' ', s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


_COMPANY_SUFFIXES = {
    'inc', 'inc.', 'llc', 'l.l.c.', 'ltd', 'ltd.', 'limited', 'gmbh', 'bv', 'b.v.', 'plc', 'pty', 'pty.',
    'corp', 'corp.', 'co', 'co.', 'company', 's.a.', 's.a', 's.a.s', 'sas', 'oy', 'ab', 'ag', 'kk', 'k.k.', 'kk.',
}


def _norm_developer_for_match(s: str) -> str:
    s = _norm_text(s)
    # remove punctuation
    s = NON_ALNUM_RE.sub(' ', s)
    parts = [p for p in s.split() if p and p not in _COMPANY_SUFFIXES]
    s = ' '.join(parts)
    return s.strip()


def _choose_text(a: str, b: str) -> str:
    a = a or ''
    b = b or ''
    if not a:
        return b
    if not b:
        return a
    # Prefer longer, otherwise keep existing
    return b if len(b.strip()) > len(a.strip()) else a


def _merge_bool_str(a: str, b: str) -> str:
    # Strings like 'true'/'false' (case-insensitive)
    va = (str(a).lower() == 'true') if a != '' else False
    vb = (str(b).lower() == 'true') if b != '' else False
    return 'true' if (va or vb) else 'false'


def _merge_list_field(a: str, b: str) -> str:
    # Merge comma-separated lists into unique comma-separated
    parts = []
    if a:
        parts.extend([p.strip() for p in str(a).split(',') if p.strip()])
    if b:
        parts.extend([p.strip() for p in str(b).split(',') if p.strip()])
    if not parts:
        return ''
    uniq = []
    seen = set()
    for p in parts:
        k = p.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return ','.join(uniq)


def map_row(row: dict, schema_cols: list, mapping: dict, platform_label: str, store_label: str):
    out = {col: '' for col in schema_cols}
    # Map fields
    for src, dst in mapping.items():
        if dst in schema_cols and src in row:
            out[dst] = row.get(src, '')
    # Add platform/store labels
    if 'Platform_Technology' in schema_cols:
        # Keep original behavior; can be adjusted to 'Mobile' later if desired
        out['Platform_Technology'] = platform_label
    if 'store' in schema_cols:
        out['store'] = store_label
    return out


def combine(appstore_path: str, playstore_path: str, schema_path: str, output_prefix: str = 'COMBINED_apps'):
    schema_cols = read_schema_columns(schema_path)

    # Read sources
    appstore_fields, appstore_rows = read_csv_dicts(appstore_path)
    playstore_fields, playstore_rows = read_csv_dicts(playstore_path)

    # Diagnostics: show which mapping keys are present
    def _present_keys(fields, mapping):
        return [k for k in mapping.keys() if k in fields]
    print("App Store columns present that we map:", _present_keys(appstore_fields, APP_STORE_MAPPING))
    print("Play Store columns present that we map:", _present_keys(playstore_fields, PLAY_STORE_MAPPING))

    # Map rows separately (no field merges)
    ios_rows = [
        map_row(r, schema_cols, APP_STORE_MAPPING, platform_label='iOS', store_label='Apple App Store')
        for r in appstore_rows
    ]
    and_rows = [
        map_row(r, schema_cols, PLAY_STORE_MAPPING, platform_label='Android', store_label='Google Play Store')
        for r in playstore_rows
    ]

    combined = ios_rows + and_rows

    # Build clusters so duplicates (by id OR by normalized title+developer) are adjacent
    def _nd_key(row):
        return f"nd:{_norm_title_for_match(row.get('App_Name'))}||{_norm_developer_for_match(row.get('developer'))}"
    def _id_key(row):
        idv = (row.get('id') or '').strip().lower()
        return f"id:{idv}" if idv else ''

    rep_by_key = {}
    keys_in_rep = {}
    cluster_order = {}
    row_cluster_rep = []
    next_order = 0

    def _ensure_rep(keys):
        nonlocal next_order
        # find existing reps
        reps = [rep_by_key[k] for k in keys if k and k in rep_by_key]
        if not reps:
            # new cluster; prefer non-empty nd key else id key else fallback
            rep = next((k for k in keys if k), f"misc:{next_order}")
            rep_by_key.update({k: rep for k in keys if k})
            keys_in_rep[rep] = set(k for k in keys if k)
            cluster_order.setdefault(rep, next_order)
            next_order += 1
            return rep
        # choose canonical rep (smallest lexicographically to stabilize)
        rep = min(reps)
        # merge all into canonical rep
        for r in reps:
            if r == rep:
                continue
            for k in keys_in_rep.get(r, []):
                rep_by_key[k] = rep
            keys_in_rep.setdefault(rep, set()).update(keys_in_rep.get(r, []))
            # drop old
            if r in keys_in_rep:
                del keys_in_rep[r]
        # ensure current keys are assigned
        for k in keys:
            if k:
                rep_by_key[k] = rep
                keys_in_rep.setdefault(rep, set()).add(k)
        # preserve earliest order
        if rep not in cluster_order:
            cluster_order[rep] = next_order
            next_order += 1
        return rep

    for row in combined:
        keys = [_nd_key(row), _id_key(row)]
        rep = _ensure_rep(keys)
        row_cluster_rep.append(rep)

    # Determine availability per cluster (has iOS and Android rows)
    cluster_has_ios = {}
    cluster_has_and = {}
    for row, rep in zip(combined, row_cluster_rep):
        st = (row.get('store') or '').lower()
        if 'apple' in st:
            cluster_has_ios[rep] = True
        if 'google' in st:
            cluster_has_and[rep] = True

    # Annotate per row using cluster membership
    for i, row in enumerate(combined):
        rep = row_cluster_rep[i]
        is_both = cluster_has_ios.get(rep, False) and cluster_has_and.get(rep, False)
        if 'availableOnBothPlatforms' in row:
            row['availableOnBothPlatforms'] = 'true' if is_both else 'false'
        if is_both:
            row['store'] = 'Both'
            if 'platforms' in row and not row.get('platforms'):
                row['platforms'] = 'iOS|Android'
        if not row.get('App_Name'):
            row['App_Name'] = row.get('id', '')

    # Sort rows so duplicates are adjacent: by cluster order, then store/dev/name
    def _store_rank(s: str) -> int:
        s = (s or '').lower()
        if s == 'both':
            return 0
        if 'apple' in s:
            return 1
        if 'google' in s:
            return 2
        return 3

    combined = [r for _, r in sorted(
        zip(row_cluster_rep, combined),
        key=lambda t: (
            cluster_order.get(t[0], 1_000_000),
            _store_rank(t[1].get('store')),
            (t[1].get('developer') or '').lower(),
            (t[1].get('App_Name') or '').lower(),
        )
    )]

    # Export
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%fZ')[:-3] + 'Z'
    out_schema_csv = f"{output_prefix}_{timestamp}.csv"
    out_json = f"{output_prefix}_{timestamp}.json"
    out_simple_csv = f"{output_prefix}_{timestamp}_simple.csv"
    out_excel_csv = f"{output_prefix}_{timestamp}_excel.csv"

    # Semicolon CSV following AppsSchema (minus dropped cols)
    with open(out_schema_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=schema_cols, delimiter=';')
        writer.writeheader()
        writer.writerows(combined)

    # JSON
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    # Simple CSV (comma)
    with open(out_simple_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=schema_cols)
        writer.writeheader()
        writer.writerows(combined)

    # Excel-friendly CSV: quote-all and remove control/newline chars
    _CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\u2028\u2029]")

    def _clean_cell(s: str) -> str:
        if s is None:
            return ''
        s = str(s).replace('\r', ' ').replace('\n', ' ')
        s = _CONTROL_CHARS_RE.sub(' ', s)
        while '  ' in s:
            s = s.replace('  ', ' ')
        return s.strip()

    with open(out_excel_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writerow(schema_cols)
        for row in combined:
            writer.writerow([_clean_cell(row.get(col, '')) for col in schema_cols])

    return out_schema_csv, out_json, out_simple_csv, out_excel_csv, len(combined)


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Resolve schema path in current dir or one level up
    cand = [
        os.path.join(base_dir, 'AppsSchemaCSV.csv'),
        os.path.join(base_dir, 'AppsSchema.csv'),
        os.path.join(os.path.dirname(base_dir), 'AppsSchemaCSV.csv'),
        os.path.join(os.path.dirname(base_dir), 'AppsSchema.csv'),
    ]
    schema_path = next((p for p in cand if os.path.exists(p)), None)
    appstore_path = os.path.join(base_dir, 'AppStoreAppsCSV.csv')
    playstore_path = os.path.join(base_dir, 'PlayStoreAppsCSV.csv')

    if not schema_path or not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found (expected AppsSchemaCSV.csv or AppsSchema.csv in {base_dir})")
    if not os.path.exists(appstore_path):
        raise FileNotFoundError(f"AppStore CSV not found: {appstore_path}")
    if not os.path.exists(playstore_path):
        raise FileNotFoundError(f"PlayStore CSV not found: {playstore_path}")

    out1, out2, out3, out4, n = combine(appstore_path, playstore_path, schema_path)
    print(f"Exported {n} rows:\n  - {out1}\n  - {out2}\n  - {out3}\n  - {out4}")
