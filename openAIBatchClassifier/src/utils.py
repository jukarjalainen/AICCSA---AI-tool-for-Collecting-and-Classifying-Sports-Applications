import os, json, time, re
from typing import Iterable, List, Any

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def chunks(items: List[Any], size: int) -> Iterable[List[Any]]:
    for i in range(0, len(items), size):
        yield items[i:i+size]

def looks_like_track_id(s: str) -> bool:
    return bool(re.fullmatch(r"\d{6,}", s or ""))

def write_jsonl(path: str, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def read_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def backoff_sleep(attempt: int, base: float):
    time.sleep(base * (attempt + 1))
