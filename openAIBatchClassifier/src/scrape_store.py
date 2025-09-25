import os, json, requests
from google_play_scraper import app as gp_app
from tqdm import tqdm
from . import config, read_table
from .utils import ensure_dir, looks_like_track_id, write_jsonl, backoff_sleep

CACHE_PATH = os.path.join(config.OUT_DIR, "desc_cache.json")

def _load_cache():
    """Retrieve the cached descriptions map from disk (if present)."""
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_cache(cache: dict):
    """Persist the descriptions cache so subsequent runs can reuse results."""
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)

def get_desc_android(pkg: str, cache: dict) -> str:
    """Fetch an Android app's description, consulting cache and retries."""
    key = f"Android::{pkg}"
    if key in cache:
        return cache[key]
    desc = ""
    for attempt in range(config.MAX_RETRIES):
        try:
            meta = gp_app(pkg, lang="en", country="us")
            desc = meta.get("description") or ""
            break
        except Exception:
            backoff_sleep(attempt, config.RETRY_BACKOFF_SEC)
    cache[key] = desc
    return desc

def get_desc_ios(app_id: str, cache: dict) -> str:
    """Fetch an iOS app's description, toggling between track ID and bundle lookups."""
    key = f"iOS::{app_id}"
    if key in cache:
        return cache[key]
    if looks_like_track_id(app_id):
        url = f"https://itunes.apple.com/lookup?id={app_id}"
    else:
        url = f"https://itunes.apple.com/lookup?bundleId={app_id}"
    desc = ""
    for attempt in range(config.MAX_RETRIES):
        try:
            r = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            desc = (data.get("results") or [{}])[0].get("description", "") or ""
            break
        except Exception:
            backoff_sleep(attempt, config.RETRY_BACKOFF_SEC)
    cache[key] = desc
    return desc

def run_scrape():
    """Main entry point: gather descriptions for apps listed in the source table."""
    ensure_dir(config.OUT_DIR)
    df = read_table.read_app_table()
    rows = df.to_dict(orient="records")

    cache = _load_cache()
    out = []
    empty_count = 0

    for r in tqdm(rows, desc="Scraping descriptions"):
        pid = str(r["id"]).strip()
        plat = r["platform"].strip()
        if plat == "Android":
            desc = get_desc_android(pid, cache)
        else:
            desc = get_desc_ios(pid, cache)
        if not desc:
            empty_count += 1
        out.append({"id": pid, "platform": plat, "description": desc})

    _save_cache(cache)
    write_jsonl(config.DESCRIPTIONS_JSONL, out)

    print(f"Saved {len(out)} records -> {config.DESCRIPTIONS_JSONL}")
    print(f"Descriptions missing/empty: {empty_count}")

if __name__ == "__main__":
    run_scrape()
