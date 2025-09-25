import json, pandas as pd
from . import config, read_table

def parse_batch_output():
    records = []
    with open(config.BATCH_OUTPUT_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            try:
                content = obj["response"]["body"]["choices"][0]["message"]["content"]
                arr = json.loads(content)
                if isinstance(arr, list):
                    records.extend(arr)
                else:
                    records.append(arr)
            except Exception:
                continue
    return pd.DataFrame.from_records(records)

def merge_to_excel():
    base = read_table.read_app_table()  # (id, platform)
    preds = parse_batch_output()

    # normalize
    for col in ("id","platform"):
        if col in preds.columns:
            preds[col] = preds[col].astype(str).str.strip()

    want = [
        "id","platform","athlete","support_staff","supporter",
        "governing_entity","sport_type","purpose","not_relevant"
    ]
    keep = [c for c in want if c in preds.columns]
    preds = preds[keep]

    merged = base.merge(preds, on=["id","platform"], how="left")
    merged.to_excel(config.OUTPUT_XLSX, index=False)
    print("Wrote:", config.OUTPUT_XLSX)

if __name__ == "__main__":
    merge_to_excel()
