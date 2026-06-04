import os
import pandas as pd
from . import config, read_table
from .utils import ensure_dir, write_jsonl


def _is_unclassified(row: dict) -> bool:
    """Check if a row is missing AI classification fields.
    
    A row is unclassified if any core classification field is truly absent/empty/NaN.
    """
    import pandas as pd
    
    # Core AI classification fields that MUST have a non-NaN value
    # NOTE: Column names from output have mixed case (Purpose, Sport_Type)
    required_fields = ["not_relevant", "Purpose", "Sport_Type"]
    
    for field in required_fields:
        val = row.get(field)
        
        # pandas.isna() covers NaN, None, pd.NaT, etc.
        if pd.isna(val):
            return True
        
        # Also check for string representations of empty
        val_str = str(val).strip()
        if not val_str or val_str.lower() in ("nan", "none", ""):
            return True
    
    return False


def identify_unclassified(input_file: str) -> pd.DataFrame:
    """Load input and return subset of rows that lack classification."""
    df = read_table._load_table(input_file)
    
    # Identify unclassified rows
    unclassified = df[df.apply(_is_unclassified, axis=1)].copy()
    
    if len(unclassified) == 0:
        print("No unclassified applications found.")
        return unclassified
    
    print(f"Found {len(unclassified)} unclassified applications (out of {len(df)})")
    return unclassified


def build_retry_descriptions(unclassified_df: str | pd.DataFrame, cache_path: str | None = None) -> None:
    """Build descriptions JSONL for unclassified apps only."""
    from .scrape_store import get_desc_android, get_desc_ios, _load_cache, _save_cache
    
    if isinstance(unclassified_df, str):
        unclassified_df = read_table._load_table(unclassified_df)
    
    if len(unclassified_df) == 0:
        print("No unclassified rows to process.")
        return
    
    cache = _load_cache()
    out = []
    empty_count = 0
    
    for _, row in unclassified_df.iterrows():
        pid = str(row.get("id") or row.get("appId", "")).strip()
        plat_raw = str(row.get("platform", "")).strip().lower()
        
        # Normalize platform
        if "android" in plat_raw or "google" in plat_raw:
            plat = "Android"
        elif "ios" in plat_raw or "apple" in plat_raw:
            plat = "iOS"
        else:
            continue
        
        # Fetch description
        if plat == "Android":
            desc = get_desc_android(pid, cache)
        else:
            desc = get_desc_ios(pid, cache)
        
        if not desc:
            empty_count += 1
        
        out.append({"id": pid, "platform": plat, "description": desc})
    
    _save_cache(cache)
    
    # Write to a separate jsonl file for retry batch
    retry_jsonl = os.path.join(config.OUT_DIR, "descriptions_retry.jsonl")
    write_jsonl(retry_jsonl, out)
    
    print(f"Built retry descriptions: {len(out)} records -> {retry_jsonl}")
    print(f"Empty descriptions in retry: {empty_count}")


def merge_retry_results(base_file: str, first_merge_file: str, retry_output_files: list[str]) -> str:
    """Merge retry batch results back into the first-pass merged file."""
    import json
    from datetime import datetime
    
    # Load the first-pass merged file
    merged = read_table._load_table(first_merge_file)
    schema_cols = list(merged.columns)
    
    # Parse retry batch outputs
    retry_records = []
    for output_file in retry_output_files:
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                try:
                    content = obj["response"]["body"]["choices"][0]["message"]["content"]
                    # Extract JSON array
                    content = (content or "").strip()
                    start = content.find("[")
                    end = content.rfind("]")
                    if start != -1 and end != -1 and end > start:
                        try:
                            parsed = json.loads(content[start:end+1])
                            if isinstance(parsed, list):
                                retry_records.extend(parsed)
                        except Exception:
                            pass
                except Exception:
                    continue
    
    retry_df = pd.DataFrame.from_records(retry_records)
    
    if len(retry_df) == 0:
        print("No retry classification results to merge.")
        return first_merge_file
    
    print(f"Merging {len(retry_df)} retry classifications into main output...")
    
    # Normalize retry results
    for col in ("id", "platform"):
        if col in retry_df.columns:
            retry_df[col] = retry_df[col].fillna("").astype(str).str.strip()
    
    for c in ("athlete", "support_staff", "supporter", "governing_entity", "not_relevant"):
        if c in retry_df.columns:
            retry_df[c] = retry_df[c].fillna(False).astype(bool)
    
    # Convert stakeholder bools to TRUE/FALSE strings
    for group_col in ("athlete", "support_staff", "supporter", "governing_entity"):
        if group_col in retry_df.columns:
            retry_df[group_col] = retry_df[group_col].map(lambda v: "TRUE" if bool(v) else "FALSE")
        else:
            retry_df[group_col] = ""
    
    # Keep not_relevant as-is (don't convert to is_relevant)
    if "not_relevant" in retry_df.columns:
        retry_df["not_relevant"] = retry_df["not_relevant"].map(lambda v: "TRUE" if bool(v) else "FALSE")
    else:
        retry_df["not_relevant"] = ""
    
    # Ensure sport_type and purpose exist
    if "sport_type" not in retry_df.columns:
        retry_df["sport_type"] = ""
    if "purpose" not in retry_df.columns:
        retry_df["purpose"] = ""
    
    # Map to schema columns
    def _resolve_column(df, candidates):
        lowered = {c.lower(): c for c in df.columns}
        for candidate in candidates:
            resolved = lowered.get(candidate.lower())
            if resolved:
                return resolved
        return None
    
    schema_target_cols = {
        "not_relevant": _resolve_column(merged, ["not_relevant", "Not_relevant"]),
        "purpose": _resolve_column(merged, ["purpose", "Purpose"]),
        "sport_type": _resolve_column(merged, ["sport_type", "Sport_Type"]),
        "athlete": _resolve_column(merged, ["athlete", "Athlete"]),
        "supporter": _resolve_column(merged, ["supporter", "Supporter"]),
        "support_staff": _resolve_column(merged, ["support_staff", "Support_Staff"]),
        "governing_entity": _resolve_column(merged, ["governing_entity", "Governing_Entity"]),
    }
    
    # Prepare for merge
    id_col = _resolve_column(merged, ["id", "appId", "app_id", "App_ID"])
    platform_col = _resolve_column(merged, ["platform", "Platform_Technology"])
    
    if not id_col:
        raise KeyError("Merged file missing id column.")
    
    # Normalize IDs in both dataframes
    def canonical_platform(value):
        raw = (value or "").strip().lower()
        if "android" in raw or "google" in raw:
            return "Android"
        if "ios" in raw or "apple" in raw:
            return "iOS"
        return ""
    
    merged["__merge_id"] = merged[id_col].fillna("").astype(str).str.strip()
    if platform_col:
        merged["__merge_platform"] = merged[platform_col].fillna("").astype(str).map(canonical_platform)
    else:
        merged["__merge_platform"] = ""
    
    retry_df["__merge_id"] = retry_df["id"].fillna("").astype(str).str.strip()
    retry_df["__merge_platform"] = retry_df["platform"].fillna("").astype(str).map(canonical_platform)
    
    join_keys = ["__merge_id", "__merge_platform"] if platform_col else ["__merge_id"]
    retry_df = retry_df.drop_duplicates(subset=join_keys, keep="first")
    
    # Merge retry results into main file (LEFT join to keep all rows)
    target_cols = ["not_relevant", "purpose", "sport_type", "athlete", "supporter", "support_staff", "governing_entity"]
    retry_updates = retry_df[join_keys + target_cols].rename(
        columns={c: f"{c}__retry" for c in target_cols if c in retry_df.columns}
    )
    
    merged = merged.merge(retry_updates, on=join_keys, how="left")
    
    # Update blanks in main file with retry results
    for logical_col, schema_col in schema_target_cols.items():
        if not schema_col or schema_col not in merged.columns:
            continue
        retry_col = f"{logical_col}__retry"
        if retry_col not in merged.columns:
            continue
        
        merged[schema_col] = merged[schema_col].fillna("").astype(str)
        merged[retry_col] = merged[retry_col].fillna("").astype(str)
        
        # Fill empty cells in schema_col with non-empty values from retry_col
        update_mask = (merged[schema_col].str.strip() == "") & (merged[retry_col].str.strip() != "")
        merged.loc[update_mask, schema_col] = merged.loc[update_mask, retry_col]
        merged.drop(columns=[retry_col], inplace=True)
    
    # Clean up temp columns
    merged = merged.drop(columns=["__merge_id", "__merge_platform"], errors="ignore")
    merged = merged[schema_cols]
    
    # ---- Apply not_relevant logic: if not_relevant=TRUE, all classification fields should be "UNKNOWN" ----
    not_relevant_col = schema_target_cols.get("not_relevant")
    if not_relevant_col and not_relevant_col in merged.columns:
        classification_cols = [
            schema_target_cols.get(c) for c in ["purpose", "sport_type", "athlete", "supporter", "support_staff", "governing_entity"]
            if schema_target_cols.get(c) and schema_target_cols.get(c) in merged.columns
        ]
        # If not_relevant = TRUE, set all classification fields to "UNKNOWN"
        not_relevant_mask = (merged[not_relevant_col].fillna("").astype(str).str.strip().str.upper() == "TRUE")
        for col in classification_cols:
            merged.loc[not_relevant_mask, col] = "UNKNOWN"
            # Also set empty/NaN values to "UNKNOWN" for relevant apps
            merged.loc[~not_relevant_mask, col] = merged.loc[~not_relevant_mask, col].fillna("UNKNOWN").astype(str).str.strip()
            merged.loc[(~not_relevant_mask) & (merged[col] == ""), col] = "UNKNOWN"
    
    # Save merged result
    ts = datetime.now().strftime("%Y-%d-%m_%H%M")
    out_name = f"apps_with_classification_retry_{ts}.xlsx"
    out_path = os.path.join(config.OUT_DIR, out_name)
    
    merged.to_excel(out_path, index=False)
    
    # Update latest symlink
    try:
        import shutil
        shutil.copyfile(out_path, config.LATEST_CLASSIFIED_XLSX)
        print(f"Wrote (updated): {config.LATEST_CLASSIFIED_XLSX}")
    except PermissionError:
        print(f"Warning: latest_classified.xlsx is locked; using timestamped file: {out_path}")
    
    print(f"Wrote: {out_path}")
    return out_path


if __name__ == "__main__":
    # Test: identify unclassified from a merged file
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        unclass = identify_unclassified(input_file)
        print(f"Unclassified count: {len(unclass)}")
    else:
        print("Usage: python -m retry_unclassified <merged_xlsx_path>")
