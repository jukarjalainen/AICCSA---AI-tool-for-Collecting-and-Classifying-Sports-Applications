import os, json, pandas as pd
import shutil
from datetime import datetime
from . import config

def _extract_json_array(content: str):
    content = (content or "").strip()
    if not content:
        return []

    # Some responses may include markdown fences; strip down to first JSON array.
    start = content.find("[")
    end = content.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []

    try:
        parsed = json.loads(content[start : end + 1])
        if isinstance(parsed, list):
            return parsed
    except Exception:
        return []
    return []


def parse_batch_output(output_files: list[str]):
    records = []
    for output_file in output_files:
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                try:
                    content = obj["response"]["body"]["choices"][0]["message"]["content"]
                    records.extend(_extract_json_array(content))
                except Exception:
                    continue
    return pd.DataFrame.from_records(records)


def _load_table(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported input file extension: {ext}")


def _resolve_column(df: pd.DataFrame, candidates: list[str]):
    lowered = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        resolved = lowered.get(candidate.lower())
        if resolved:
            return resolved
    return None


def _canonical_platform(value: str):
    raw = (value or "").strip().lower()
    if "android" in raw or "google" in raw:
        return "Android"
    if "ios" in raw or "apple" in raw:
        return "iOS"
    return ""


def _resolve_classification_columns(df: pd.DataFrame):
    return {
        "is_relevant": _resolve_column(df, ["is_relevant", "Is_relevant"]),
        "purpose": _resolve_column(df, ["purpose", "Purpose"]),
        "stakeholder": _resolve_column(df, ["stakeholder", "Stakeholder"]),
        "sport_type": _resolve_column(df, ["sport_type", "Sport_Type"]),
    }

def merge_to_csv(input_file: str, output_files: list[str]):
    base = _load_table(input_file)
    schema_cols = list(base.columns)
    preds = parse_batch_output(output_files)

    id_col = _resolve_column(base, ["id", "appId", "app_id", "App_ID"])
    platform_col = _resolve_column(
        base,
        ["platform", "store", "targetStore", "Platform_Technology"],
    )
    app_id_col = _resolve_column(base, ["appId", "app_id", "App_ID"])

    if not id_col:
        raise KeyError("Input file is missing an app id column (e.g., id/appId/App_ID).")

    base_work = base.copy()
    base_work["__merge_id"] = base_work[id_col].fillna("").astype(str).str.strip()
    if app_id_col:
        fallback_ids = base_work[app_id_col].fillna("").astype(str).str.strip()
        base_work["__merge_id"] = base_work["__merge_id"].where(
            base_work["__merge_id"] != "",
            fallback_ids,
        )
    if platform_col:
        base_work["__merge_platform"] = (
            base_work[platform_col].fillna("").astype(str).map(_canonical_platform)
        )
    else:
        base_work["__merge_platform"] = ""

    # normalize
    for col in ("id", "platform"):
        if col in preds.columns:
            preds[col] = preds[col].fillna("").astype(str).str.strip()

    for c in ("athlete", "support_staff", "supporter", "governing_entity", "not_relevant"):
        if c in preds.columns:
            preds[c] = preds[c].fillna(False).astype(bool)

    stakeholder_parts = []
    for key in ("athlete", "support_staff", "supporter", "governing_entity"):
        if key in preds.columns:
            stakeholder_parts.append(
                preds.apply(lambda r: key if bool(r.get(key, False)) else "", axis=1)
            )

    if stakeholder_parts:
        preds["stakeholder"] = (
            pd.concat(stakeholder_parts, axis=1)
            .apply(lambda row: "|".join([v for v in row.tolist() if v]), axis=1)
        )
    else:
        preds["stakeholder"] = ""

    if "not_relevant" in preds.columns:
        preds["is_relevant"] = (~preds["not_relevant"]).map(lambda v: "TRUE" if v else "FALSE")
    else:
        preds["is_relevant"] = ""

    if "sport_type" not in preds.columns:
        preds["sport_type"] = ""
    if "purpose" not in preds.columns:
        preds["purpose"] = ""

    target_cols = ["is_relevant", "purpose", "stakeholder", "sport_type"]
    schema_target_cols = _resolve_classification_columns(base_work)

    keep = [c for c in ["id", "platform", *target_cols] if c in preds.columns]
    preds = preds[keep]
    if "id" not in preds.columns:
        raise KeyError("Batch predictions are missing required 'id' field.")

    preds["__merge_id"] = preds["id"].fillna("").astype(str).str.strip()
    if "platform" in preds.columns:
        preds["__merge_platform"] = preds["platform"].fillna("").astype(str).map(_canonical_platform)

    join_keys = ["__merge_id", "__merge_platform"] if "platform" in preds.columns else ["__merge_id"]
    preds = preds.drop_duplicates(subset=join_keys, keep="first")

    # Keep the original scraper schema and only update classification values.
    pred_updates = preds.rename(columns={c: f"{c}__new" for c in target_cols if c in preds.columns})
    merged = base_work.merge(pred_updates, on=join_keys, how="left")

    for logical_col, schema_col in schema_target_cols.items():
        if not schema_col:
            continue
        merged[schema_col] = merged[schema_col].fillna("").astype(str)
        new_col = f"{logical_col}__new"
        if new_col in merged.columns:
            merged[new_col] = merged[new_col].fillna("").astype(str)
            update_mask = merged[new_col].str.strip() != ""
            merged.loc[update_mask, schema_col] = merged.loc[update_mask, new_col]
            merged.drop(columns=[new_col], inplace=True)

    merged = merged.drop(columns=["__merge_id", "__merge_platform"], errors="ignore")
    merged = merged[schema_cols]

    # ---- timestamped output name: YYYY-DD-MM_HHMM ----
    ts = datetime.now().strftime("%Y-%d-%m_%H%M")  # year-day-month_hourminute
    out_name = f"apps_with_classification_{ts}.xlsx"
    out_path = os.path.join(config.OUT_DIR, out_name)

    merged.to_excel(out_path, index=False)
    final_path = out_path
    try:
        shutil.copyfile(out_path, config.LATEST_CLASSIFIED_XLSX)
        final_path = config.LATEST_CLASSIFIED_XLSX
        print("Wrote:", config.LATEST_CLASSIFIED_XLSX)
    except PermissionError:
        print(
            "Warning: latest_classified.xlsx is locked; "
            "using timestamped output file instead."
        )
    print("Wrote:", out_path)
    return final_path

if __name__ == "__main__":
    merge_to_csv(config.DATA_FILE, [f"{config.BATCH_OUTPUT_JSONL}1"])
