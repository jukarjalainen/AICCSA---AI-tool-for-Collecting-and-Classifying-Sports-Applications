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
    from .promts import promt4
except ImportError:  # running as a plain script from inside folder
    from promts import promt4

# --- CONFIG ---
INPUT_FILE = "appsTableClearForAI.xlsx"
OUTPUT_FILE = "apps_classified.xlsx"
FETCH_WORKERS = 5         # parallel description fetching
GPT_WORKERS = 2           # parallel GPT batch calls
BATCH_GPT_SIZE = 5        # number of apps per GPT request
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
    for idx, obj in descriptions_dict.items():
        app_id = str(obj.get("id", ""))
        desc = obj.get("description", "")
        items.append({"id": app_id, "description": desc})
        id_to_row[app_id] = idx

    instructions = promt4
    prompt = instructions + "\n\nDescriptions:\n" + json.dumps(items, indent=2)

    client = get_client()
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    print(f"GPT response status: {response}")
    
    content = response.choices[0].message.content or "[]"
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
    for item in data_iter:
        # Normalize keys to lowercase for robustness (model may return Purpose / Not_relevant variations)
        norm_item = { (k.lower() if isinstance(k,str) else k): v for k,v in item.items() }
        item_id = str(norm_item.get("id", "")).strip()
        if not item_id:
            continue
        original_idx = id_to_row.get(item_id)
        if original_idx is None:
            continue
        output[original_idx] = norm_item
    if not output and os.getenv("CLASSIFIER_DEBUG"):
        print("DEBUG: Empty classification output. Raw model content:\n" + raw[:800])
    return output



# --- MAIN FUNCTION ---
BASE_DIR = os.path.dirname(__file__)
CLASS_COLUMNS = [
    "athlete", "support_staff", "supporter", "governing_entity",
    "game", "sport_type", "Purpose", "not_relevant", "description_missing"
]

def _abs(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)

def main(test_rows=None):
    if not os.getenv("OPENAI_API_KEY"):
        print("⛔ OPENAI_API_KEY not set. Set it before running. Example PowerShell: $env:OPENAI_API_KEY='sk-...' ")
        return

    # Always load the full original input file
    source_df = pd.read_excel(_abs(INPUT_FILE))
    print(f"Loaded input {INPUT_FILE} with {len(source_df)} rows")

    # If prior output exists, load for merging classification columns only
    existing_df = None
    try:
        existing_df = pd.read_excel(_abs(OUTPUT_FILE))
        print(f"Found existing output {OUTPUT_FILE} with {len(existing_df)} rows; will merge classifications.")
    except FileNotFoundError:
        pass

    # Ensure classification columns exist on source
    for col in CLASS_COLUMNS:
        if col not in source_df.columns:
            source_df[col] = None

    # Merge existing classification values by id (if both have id column)
    if existing_df is not None and 'id' in existing_df.columns and 'id' in source_df.columns:
        # Only take classification-related columns present in existing
        existing_cls_cols = [c for c in CLASS_COLUMNS if c in existing_df.columns]
        if existing_cls_cols:
            existing_map = existing_df.set_index('id')[existing_cls_cols]
            mask = source_df['id'].isin(existing_map.index)
            overlap_count = mask.sum()
            if overlap_count:
                source_df.loc[mask, existing_cls_cols] = existing_map.reindex(source_df.loc[mask,'id']).values
                print(f"Restored existing classification for {overlap_count} rows")

    # Build list of indices needing classification
    def needs_classification(row):
        # Only require core prediction columns; allow flags to remain False
        core = ["athlete","support_staff","supporter","governing_entity","game","sport_type","Purpose"]
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
                target_cols = CLASS_COLUMNS
                needs_classification = any(pd.isna(row.get(c)) or row.get(c) in (None, "") for c in target_cols)
                if not needs_classification:
                    continue
                plat_val = row["platform"] if "platform" in source_df.columns else None
                app_id = str(row["id"]) if "id" in source_df.columns else None
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
        for i, d in descriptions.items():
            if isinstance(d, str) and d.strip():
                cleaned[i] = {"id": row_to_appid.get(i), "description": d}
            else:
                # Mark description missing and do not alter other cells
                source_df.at[i, "description_missing"] = True
        descriptions = cleaned
        if not descriptions:
            continue

        # --- GPT BATCH CLASSIFICATION ---
        try:
            batch_results = classify_descriptions_batch(descriptions)
            if not batch_results and os.getenv('CLASSIFIER_DEBUG'):
                print('DEBUG: No batch_results returned for indices', batch_indices)
            for idx, result in batch_results.items():
                source_df.at[idx, "athlete"] = bool(result.get("athlete")) if result.get("athlete") is not None else False
                source_df.at[idx, "support_staff"] = bool(result.get("support_staff")) if result.get("support_staff") is not None else False
                source_df.at[idx, "supporter"] = bool(result.get("supporter")) if result.get("supporter") is not None else False
                source_df.at[idx, "governing_entity"] = bool(result.get("governing_entity")) if result.get("governing_entity") is not None else False
                source_df.at[idx, "game"] = bool(result.get("game")) if result.get("game") is not None else False
                source_df.at[idx, "sport_type"] = normalize_sport_type(result.get("sport_type"))
                source_df.at[idx, "Purpose"] = normalize_purpose(result.get("purpose"))
                source_df.at[idx, "not_relevant"] = bool(result.get("not_relevant")) if result.get("not_relevant") is not None else False
                if not source_df.at[idx, "description_missing"]:
                    source_df.at[idx, "description_missing"] = bool(result.get("description_missing"))
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
