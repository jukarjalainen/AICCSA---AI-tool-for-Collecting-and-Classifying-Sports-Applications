import json
from . import config
from .utils import ensure_dir, read_jsonl, chunks

def load_prompt_text():
    with open(config.PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def validate_descriptions(strict: bool = True):
    total, empties = 0, 0
    for rec in read_jsonl(config.DESCRIPTIONS_JSONL):
        total += 1
        if not (rec.get("description") or "").strip():
            empties += 1
    if strict and empties > 0:
        raise RuntimeError(f"Found {empties} empty descriptions out of {total}. "
                           f"Fix or re-scrape before building batch.")
    return total, empties

def build_batch_input():
    ensure_dir(config.OUT_DIR)
    prompt = load_prompt_text()
    records = list(read_jsonl(config.DESCRIPTIONS_JSONL))
    requests = list(chunks(records, config.CHUNK_SIZE))
    files_written = []
    global_chunk_idx = 1

    for file_idx, req_group in enumerate(
        chunks(requests, config.MAX_REQUESTS_PER_FILE),
        start=1,
    ):
        out_path = f"{config.BATCH_INPUT_JSONL}{file_idx}"
        with open(out_path, "w", encoding="utf-8") as f:
            for group in req_group:
                payload = [
                    {
                        "id": r["id"],
                        "platform": r["platform"],
                        "description": r.get("description", ""),
                    }
                    for r in group
                ]
                custom_id = f"chunk_{global_chunk_idx:05d}"
                line = {
                    "custom_id": custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": config.MODEL,
                        "temperature": config.TEMPERATURE,
                        "messages": [
                            {"role": "system", "content": prompt},
                            {
                                "role": "user",
                                "content": json.dumps(payload, ensure_ascii=False),
                            },
                        ],
                    },
                }
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
                global_chunk_idx += 1

        files_written.append(out_path)
        print(f"Wrote Batch input: {out_path}")

    return files_written

if __name__ == "__main__":
    validate_descriptions(strict=True)
    build_batch_input()
