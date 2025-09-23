import os
import pandas as pd
from openai import OpenAI
from google_play_scraper import app as gp_app
import time, random, json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Robust import of prompt template whether run as module or script
try:
    from .promts import promt7 as system_promt
except ImportError:  # running as a plain script from inside folder
    from promts import promt7 as system_promt

# --- CONFIG ---
INPUT_FILE = "appsTableClearForAI.xlsx"
OUTPUT_FILE = "apps_classified.xlsx"
FETCH_WORKERS = 5         # parallel description fetching
GPT_WORKERS = 2           # parallel GPT batch calls
BATCH_GPT_SIZE = 200      # number of apps per GPT request
MAX_RETRIES = 3
SLEEP_TIME = 0.2
OPENAI_MODEL = "gpt-5-mini"

# Defer client creation until after we confirm key exists
_client_instance = None
def get_client():
    global _client_instance
    if _client_instance is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY environment variable not set. In PowerShell: $env:OPENAI_API_KEY='your_key'")
        _client_instance = OpenAI()
    return _client_instance

# --- NORMALIZATION HELPERS ---
CANONICAL_PURPOSES = [
    "Betting",
    "Betting tips",
    "Health tips",
    "League management",
    "Live updates",
    "Multi purpose",
    "News",
    "Radio",
    "Social network",
    "Streaming",
    "Team management",
    "Tools",
    "Tracking",
    "Training",
    "Fantasy sports",
    "Nutrition planning",
    "UNKNOWN",
]

def _norm_key(s: str) -> str:
    return " ".join(str(s or "").strip().replace("_", " ").split()).lower()

_PURPOSE_MAP = { _norm_key(p): p for p in CANONICAL_PURPOSES }

def normalize_purpose(value) -> str:
    if value is None:
        return "UNKNOWN"
    s = str(value)
    if s.upper() == "UNKNOWN":
        return "UNKNOWN"
    key = _norm_key(s)
    return _PURPOSE_MAP.get(key, s)

def normalize_sport_type(value) -> str:
    if value is None:
        return "UNKNOWN"
    s = str(value).strip()
    if not s:
        return "UNKNOWN"
    if s.upper() == "UNKNOWN":
        return "UNKNOWN"
    # Convert common underscore forms
    s2 = " ".join(s.replace("_", " ").split())
    return s2

# --- RETRY DECORATOR ---
def with_retries(func):
    def wrapper(*args, **kwargs):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                wait = 2 ** attempt + random.random()
                print(f"⚠️ Error in {func.__name__}: {e}. Retry {attempt}/{MAX_RETRIES} after {wait:.1f}s")
                time.sleep(wait)
        print(f"❌ Failed after {MAX_RETRIES} retries: {func.__name__}")
        return None
    return wrapper

# --- FETCH DESCRIPTION ---
@with_retries
def fetch_description(app_id, platform=None):
    # Helper: Apple lookup
    def apple_lookup_description(app_identifier):
        base = "https://itunes.apple.com/lookup"
        s = str(app_identifier).strip()
        # Prefer English descriptions without forcing a single storefront.
        # Try common English storefronts first with lang=en-us, then fall back.
        english_countries = ["us", "gb", "ca", "au", "ie", "sg", "nz"]
        for c in english_countries:
            params = {"bundleId": s, "country": c, "lang": "en-us"}
            try:
                r = requests.get(base, params=params, timeout=15)
            except Exception:
                continue
            if r.status_code != 200:
                continue
            try:
                data = r.json()
            except Exception:
                continue
            if not data or int(data.get("resultCount", 0)) == 0:
                continue
            item = data["results"][0]
            desc = item.get("description", "") or item.get("releaseNotes", "") or ""
            if isinstance(desc, str) and desc.strip():
                return desc

        # Fallback: no explicit country or language
        try:
            r = requests.get(base, params={"bundleId": s}, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data and int(data.get("resultCount", 0)) > 0:
                    item = data["results"][0]
                    desc = item.get("description", "") or item.get("releaseNotes", "") or ""
                    if isinstance(desc, str) and desc.strip():
                        return desc
        except Exception:
            pass
        return ""

    plat = (platform or "").strip().lower() if isinstance(platform, str) else None
    if plat == "android":
        result = gp_app(app_id, lang="en")
        return result.get("description", "")
    elif plat == "ios":
        # Use Apple's iTunes Lookup API to get the app metadata
        return apple_lookup_description(app_id)
    else:
        # Auto mode: try Android first, then Apple
        try:
            result = gp_app(app_id, lang="en")
            desc = result.get("description", "")
            if isinstance(desc, str) and desc.strip():
                return desc
        except Exception:
            pass
        return apple_lookup_description(app_id)
    return ""

# --- BATCH GPT CLASSIFICATION ---
@with_retries
def classify_descriptions_batch(descriptions_dict):
    """
    descriptions_dict: {row_index: {"id": app_id (bundleId str), "description": str}, ...}
    Returns: {row_index: classification_dict, ...}
    """
    items = []
    id_to_row = {}
    original_id_mapping = {}  # Track original vs normalized IDs
    
    for idx, obj in descriptions_dict.items():
        app_id = str(obj.get("id", "")).strip()
        desc = obj.get("description", "")
        
        # Clean and normalize ID for robust matching
        normalized_id = app_id.lower().strip().strip('"').strip("'")
        
        items.append({"id": app_id, "description": desc})  # Send original ID
        id_to_row[normalized_id] = idx
        original_id_mapping[app_id] = normalized_id
        
    instructions = system_promt
    items_payload = json.dumps(items, separators=(",",":"))  # minified JSON array

    client = get_client()
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "system", "content": instructions},
                  {"role": "user", "content": items_payload}]
    )

    # Debug-safe printing of returned choices (some API calls return only 1 choice)
    if os.getenv("CLASSIFIER_DEBUG"):
        for i, ch in enumerate(response.choices):
            try:
                snippet = (ch.message.content or "").strip()
                print(f"DEBUG choice[{i}] len={len(snippet)} preview={(snippet[:140] + '...') if len(snippet) > 140 else snippet}")
            except Exception as e:
                print(f"DEBUG failed reading choice {i}: {e}")

    # Use the first non-empty content among choices
    content = "[]"
    for ch in response.choices:
        c = (getattr(ch, 'message', None) and ch.message.content) or ""
        if isinstance(c, str) and c.strip():
            content = c
            break
    # If model returns an error wrapper telling us it wants an array, build array ourselves from input skeleton.
    if '"error"' in content.lower() and 'json array' in content.lower():
        # create empty default array to avoid full failure; downstream will see empty and skip
        if os.getenv('CLASSIFIER_DEBUG'):
            print('DEBUG: Model returned error about JSON array; returning empty list for this batch.')
        content = '[]'
    raw = content
    try:
        data = json.loads(raw)
    except Exception:
        data = []

    # Accept patterns:
    # 1) list directly
    # 2) dict of id -> obj
    # 3) dict with single key whose value is list (e.g., {"results":[...]})
    data_iter = []
    if isinstance(data, list):
        data_iter = data
    elif isinstance(data, dict):
        # wrapper list under any single key
        if len(data) == 1:
            only_val = next(iter(data.values()))
            if isinstance(only_val, list):
                data_iter = only_val
        if not data_iter:  # treat as id->obj mapping
            for k, v in data.items():
                if isinstance(v, dict):
                    v = dict(v)
                    v.setdefault("id", k)
                    data_iter.append(v)

    output = {}
    matched_count = 0
    unmatched_ids = []
    
    for item in data_iter:
        # Normalize keys to lowercase for robustness (model may return Purpose / Not_relevant variations)
        norm_item = { (k.lower() if isinstance(k,str) else k): v for k,v in item.items() }
        item_id = str(norm_item.get("id", "")).strip()
        if not item_id:
            continue
            
        # Try multiple normalization strategies for robust matching
        normalized_candidates = [
            item_id.lower().strip().strip('"').strip("'"),  # primary normalization
            item_id.lower().strip(),  # basic case normalization
            item_id.strip(),  # preserve case, remove whitespace
        ]
        
        original_idx = None
        for candidate in normalized_candidates:
            if candidate in id_to_row:
                original_idx = id_to_row[candidate]
                matched_count += 1
                break
                
        if original_idx is not None:
            output[original_idx] = norm_item
        else:
            unmatched_ids.append(item_id)
            
    if os.getenv("CLASSIFIER_DEBUG"):
        if not output:
            print("DEBUG: Empty classification output. Raw model content:\n" + raw[:800])
        else:
            print(f"DEBUG: Matched {matched_count}/{len(data_iter)} items")
            if unmatched_ids:
                print(f"DEBUG: {len(unmatched_ids)} unmatched IDs from API response:")
                for uid in unmatched_ids[:5]:  # Show first 5 unmatched IDs
                    print(f"  - '{uid}'")
                print(f"DEBUG: Available ID mapping keys (first 5):")
                for key in list(id_to_row.keys())[:5]:
                    print(f"  - '{key}'")
    return output

# --- MAIN FUNCTION ---
BASE_DIR = os.path.dirname(__file__)
# Exact column names already present in appsTableClearForAI.xlsx
EXCEL_CLASS_COLUMNS = [
    "Athlete", "Support_staff", "Supporter", "Governing_entity",
    "Game", "Sport_Type", "Purpose", "Not_relevant", "description_missing"
]

# Mapping from model keys to Excel column names
MODEL_TO_EXCEL_COL = {
    "athlete": "Athlete",
    "support_staff": "Support_staff",
    "supporter": "Supporter",
    "governing_entity": "Governing_entity",
    "game": "Game",
    "sport_type": "Sport_Type",
    "purpose": "Purpose",
    "not_relevant": "Not_relevant",
    "description_missing": "description_missing",
}

def _abs(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)

def main(test_rows=None):
    if not os.getenv("OPENAI_API_KEY"):
        print("⛔ OPENAI_API_KEY not set. Set it before running. Example PowerShell: $env:OPENAI_API_KEY='sk-...' ")
        return

    # Always load the full original input file
    source_df = pd.read_excel(_abs(INPUT_FILE))
    # Determine the key (id) column from common alternatives without adding a new column
    alt_id_cols = [
        'id', 'bundleId', 'bundle_id', 'appId', 'app_id', 'package', 'package_name', 'packageId'
    ]
    present = [c for c in alt_id_cols if c in source_df.columns]
    if not present:
        raise RuntimeError("No id-like column found (expected one of: id, bundleId, appId, package, package_name)")
    key_col = present[0]
    # normalize a temporary series for mapping
    key_series = source_df[key_col].astype(str).str.strip()
    print(f"Loaded input {INPUT_FILE} with {len(source_df)} rows")

    # If prior output exists, load for merging classification columns only
    existing_df = None
    try:
        existing_df = pd.read_excel(_abs(OUTPUT_FILE))
        print(f"Found existing output {OUTPUT_FILE} with {len(existing_df)} rows; will merge classifications.")
    except FileNotFoundError:
        pass

    # Validate required classification columns already exist (do not create new columns)
    missing = [c for c in EXCEL_CLASS_COLUMNS if c not in source_df.columns]
    if missing:
        print(f"⛔ Missing expected columns in input: {missing}. Please add them to the Excel. Aborting to avoid creating new columns.")
        return

    # Enforce stable dtypes to avoid pandas warnings and future errors
    bool_cols = ["Athlete","Support_staff","Supporter","Governing_entity","Game","Not_relevant","description_missing"]
    text_cols = ["Sport_Type","Purpose"]
    for c in bool_cols:
        if c in source_df.columns:
            try:
                source_df[c] = source_df[c].astype('boolean')
            except Exception:
                pass
    for c in text_cols:
        if c in source_df.columns:
            try:
                source_df[c] = source_df[c].astype('string')
            except Exception:
                pass

    # Merge existing classification values by the detected key column, if possible
    if False and existing_df is not None:  # Temporarily disabled to test ID matching
        existing_present = [c for c in alt_id_cols if c in existing_df.columns]
        existing_key_col = None
        # prefer same key name; else any common id-like column
        if key_col in existing_present:
            existing_key_col = key_col
        else:
            for c in existing_present:
                # choose the first id-like column that likely matches values
                existing_key_col = c
                break
        if existing_key_col is not None:
            existing_cls_cols = [c for c in EXCEL_CLASS_COLUMNS if c in existing_df.columns]
            if existing_cls_cols:
                existing_map = existing_df.set_index(existing_key_col)[existing_cls_cols]
                mask = key_series.isin(existing_map.index)
                overlap_count = mask.sum()
                if overlap_count:
                    # align by index of source rows and handle data types
                    reindexed = existing_map.reindex(key_series[mask])
                    
                    # Copy column by column to handle different dtypes
                    for col in existing_cls_cols:
                        if col in reindexed.columns:
                            source_df.loc[mask, col] = reindexed[col].values
                    
                    print(f"Restored existing classification for {overlap_count} rows using key column '{existing_key_col}'")

    # Build list of indices needing classification
    def needs_classification(row):
        # Only require core prediction columns; allow flags to remain False
        core = ["Athlete","Support_staff","Supporter","Governing_entity","Game","Sport_Type","Purpose"]
        for c in core:
            val = row.get(c)
            if pd.isna(val) or val in (None, ""):
                return True
        return False

    needing = [i for i, r in source_df.iterrows() if needs_classification(r)]
    if test_rows is not None:
        work_indices = needing[:test_rows]
        print(f"Test mode: classifying {len(work_indices)} of {len(needing)} rows needing classification")
    else:
        work_indices = needing
        print(f"Rows needing classification: {len(work_indices)}")

    processed_count = 0
    last_saved_at = 0
    for start in range(0, len(work_indices), BATCH_GPT_SIZE):
        batch_indices = work_indices[start:start + BATCH_GPT_SIZE]
        batch_rows = source_df.loc[batch_indices]

        # --- PARALLEL DESCRIPTION FETCH ---
        fetch_jobs = {}
        with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as executor:
            row_to_appid = {}
            for idx, row in batch_rows.iterrows():
                # Only skip if ALL target outputs are already present (including Purpose)
                target_cols = EXCEL_CLASS_COLUMNS
                needs_classification = any(pd.isna(row.get(c)) or row.get(c) in (None, "") for c in target_cols)
                if not needs_classification:
                    continue
                plat_val = row["platform"] if "platform" in source_df.columns else None
                app_id = str(row[key_col])
                row_to_appid[idx] = app_id
                fetch_jobs[executor.submit(fetch_description, app_id, plat_val)] = idx

            descriptions = {}
            for future in as_completed(fetch_jobs):
                idx = fetch_jobs[future]
                try:
                    descriptions[idx] = future.result()
                except Exception as e:
                    print(f"❌ Failed fetching description for row {idx}: {e}")
                    descriptions[idx] = None

        # Handle rows with missing/empty descriptions: set defaults and exclude from GPT batch
        cleaned = {}
        missing_descriptions = []
        app_id_to_rows = {}  # Map original app_id to list of row indices
        for i, d in descriptions.items():
            if isinstance(d, str) and d.strip():
                original_app_id = str(source_df.loc[i, key_col])  # Get original app ID
                cleaned[i] = {"id": original_app_id, "description": d}
                # Track which rows have this app ID
                if original_app_id not in app_id_to_rows:
                    app_id_to_rows[original_app_id] = []
                app_id_to_rows[original_app_id].append(i)
            else:
                # Mark description missing and do not alter other cells
                source_df.at[i, "description_missing"] = True
                missing_descriptions.append(i)
                
        if os.getenv('CLASSIFIER_DEBUG') and missing_descriptions:
            print(f"DEBUG: {len(missing_descriptions)} apps with missing descriptions (indices: {missing_descriptions[:10]})")
            
        descriptions = cleaned
        if not descriptions:
            if os.getenv('CLASSIFIER_DEBUG'):
                print(f"DEBUG: No valid descriptions found in batch {batch_indices}")
            continue

        # --- GPT BATCH CLASSIFICATION ---
        try:
            if os.getenv('CLASSIFIER_DEBUG'):
                print(f"DEBUG: Sending {len(descriptions)} apps to API from batch {batch_indices}")
                
            batch_results = classify_descriptions_batch(descriptions)
            
            if os.getenv('CLASSIFIER_DEBUG'):
                print(f"DEBUG: API returned {len(batch_results)} results for {len(descriptions)} sent")
                sent_indices = set(descriptions.keys())
                returned_indices = set(batch_results.keys())
                missing_results = sent_indices - returned_indices
                if missing_results:
                    print(f"DEBUG: {len(missing_results)} sent apps got no results (indices: {list(missing_results)[:10]})")
                    
            if not batch_results and os.getenv('CLASSIFIER_DEBUG'):
                print('DEBUG: No batch_results returned for indices', batch_indices)
                
            # Apply results to all rows with the same app ID
            processed_app_ids = set()
            for idx, result in batch_results.items():
                original_app_id = str(source_df.loc[idx, key_col])
                
                # Skip if we already processed this app ID (for duplicate handling)
                if original_app_id in processed_app_ids:
                    continue
                processed_app_ids.add(original_app_id)
                
                # Find all rows in current batch with this app ID and apply classification
                matching_rows = [i for i in batch_indices if str(source_df.loc[i, key_col]) == original_app_id]
                
                for row_idx in matching_rows:
                    # Booleans
                    athlete_b = bool(result.get("athlete")) if result.get("athlete") is not None else False
                    support_staff_b = bool(result.get("support_staff")) if result.get("support_staff") is not None else False
                    supporter_b = bool(result.get("supporter")) if result.get("supporter") is not None else False
                    governing_b = bool(result.get("governing_entity")) if result.get("governing_entity") is not None else False
                    game_b = bool(result.get("game")) if result.get("game") is not None else False

                    source_df.at[row_idx, "Athlete"] = athlete_b
                    source_df.at[row_idx, "Support_staff"] = support_staff_b
                    source_df.at[row_idx, "Supporter"] = supporter_b
                    source_df.at[row_idx, "Governing_entity"] = governing_b
                    source_df.at[row_idx, "Game"] = game_b

                    # Texts
                    source_df.at[row_idx, "Sport_Type"] = normalize_sport_type(result.get("sport_type"))
                    source_df.at[row_idx, "Purpose"] = normalize_purpose(result.get("purpose"))

                    # Flags
                    source_df.at[row_idx, "Not_relevant"] = bool(result.get("not_relevant")) if result.get("not_relevant") is not None else False
        except Exception as e:
            print(f"❌ GPT batch failed: {e}")

        processed_count += len(batch_indices)
        if processed_count - last_saved_at >= 100:
            source_df.to_excel(_abs(OUTPUT_FILE), index=False)
            last_saved_at = processed_count
            time.sleep(SLEEP_TIME)

    # Final save of full dataset
    try:
        source_df.to_excel(_abs(OUTPUT_FILE), index=False)
    except PermissionError:
        alt = _abs(f"apps_classified_{int(time.time())}.xlsx")
        print(f"⚠️ Permission denied writing {OUTPUT_FILE}; wrote fallback {os.path.basename(alt)}")
        source_df.to_excel(alt, index=False)
    time.sleep(SLEEP_TIME)

    print(f"🎉 Classification completed! Saved {len(source_df)} total rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Classify app rows via OpenAI")
    parser.add_argument("--test-rows", "-n", type=int, default=None, help="Limit to first N rows")
    parser.add_argument("--input", type=str, default=None, help="Override input Excel path")
    parser.add_argument("--output", type=str, default=None, help="Override output Excel path")
    args = parser.parse_args()
    if args.input:
        INPUT_FILE = args.input
    if args.output:
        OUTPUT_FILE = args.output
    main(test_rows=args.test_rows)
