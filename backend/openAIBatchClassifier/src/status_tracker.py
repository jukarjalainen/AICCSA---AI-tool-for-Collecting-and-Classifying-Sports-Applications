import json
from datetime import datetime
from . import config


def _iso_now():
    return datetime.utcnow().isoformat() + "Z"


def _read_status():
    try:
        with open(config.BATCH_STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_status(payload: dict):
    with open(config.BATCH_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def init_status(input_file: str, model: str, batch_input_files: list[str]):
    payload = {
        "status": "running",
        "stage": "uploading",
        "updatedAt": _iso_now(),
        "inputFile": input_file,
        "model": model,
        "outputFile": None,
        "error": None,
        "batches": [
            {
                "index": idx,
                "inputFile": path,
                "batchId": None,
                "status": "queued",
                "outputFile": None,
            }
            for idx, path in enumerate(batch_input_files, start=1)
        ],
    }
    _write_status(payload)


def update_batch(index: int, **fields):
    status = _read_status()
    batches = status.get("batches", [])
    for batch in batches:
        if batch.get("index") == index:
            batch.update(fields)
            break
    status["updatedAt"] = _iso_now()
    _write_status(status)


def update_stage(stage: str, status_value: str = "running"):
    status = _read_status()
    status["stage"] = stage
    status["status"] = status_value
    status["updatedAt"] = _iso_now()
    _write_status(status)


def mark_completed(output_file: str):
    status = _read_status()
    status["status"] = "completed"
    status["stage"] = "completed"
    status["outputFile"] = output_file
    status["updatedAt"] = _iso_now()
    _write_status(status)


def mark_failed(error_message: str):
    status = _read_status()
    status["status"] = "error"
    status["stage"] = "error"
    status["error"] = error_message
    status["updatedAt"] = _iso_now()
    _write_status(status)
