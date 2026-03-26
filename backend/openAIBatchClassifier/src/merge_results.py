import os, json, pandas as pd
import shutil
from datetime import datetime
from . import config, read_table

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

def merge_to_csv(input_file: str, output_files: list[str]):
    base = read_table.read_app_table(input_file=input_file, ids_only=False)
    preds = parse_batch_output(output_files)

    # normalize
    for col in ("id", "platform"):
        if col in base.columns:
            base[col] = base[col].astype(str).str.strip()
        if col in preds.columns:
            preds[col] = preds[col].astype(str).str.strip()

    want = [
        "id","platform","athlete","support_staff","supporter",
        "governing_entity","sport_type","purpose","not_relevant"
    ]
    keep = [c for c in want if c in preds.columns]
    preds = preds[keep]

    merged = base.merge(preds, on=["id","platform"], how="left")

    # ---- timestamped output name: YYYY-DD-MM_HHMM ----
    ts = datetime.now().strftime("%Y-%d-%m_%H%M")  # year-day-month_hourminute
    out_name = f"apps_with_classification_{ts}.csv"
    out_path = os.path.join(config.OUT_DIR, out_name)

    merged.to_csv(out_path, index=False)
    shutil.copyfile(out_path, config.LATEST_CLASSIFIED_CSV)
    print("Wrote:", config.LATEST_CLASSIFIED_CSV)
    print("Wrote:", out_path)
    return config.LATEST_CLASSIFIED_CSV

if __name__ == "__main__":
    merge_to_csv(config.DATA_FILE, [f"{config.BATCH_OUTPUT_JSONL}1"])
