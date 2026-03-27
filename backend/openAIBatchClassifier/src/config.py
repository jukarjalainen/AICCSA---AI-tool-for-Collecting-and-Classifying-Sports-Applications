import os

# Base paths (resolve relative to this package)
PKG_ROOT = os.path.dirname(os.path.dirname(__file__))  # .../openAIBatchClassifier
BACKEND_ROOT = os.path.dirname(PKG_ROOT)  # .../backend
PROMPTS_DIR = os.path.join(PKG_ROOT, "promts")
DATA_DIR = os.path.join(PKG_ROOT, "data")
OUT_DIR = os.path.join(PKG_ROOT, "out")

# ---------- Files ----------
DATA_FILE = os.path.join(DATA_DIR, "apps.xlsx")
DATA_XLSX = DATA_FILE
PROMPT_FILE = os.path.join(PROMPTS_DIR, "classifier_promt.txt")
DESCRIPTIONS_JSONL = os.path.join(OUT_DIR, "descriptions.jsonl")
BATCH_INPUT_JSONL = os.path.join(OUT_DIR, "batch_input.jsonl")
BATCH_OUTPUT_JSONL = os.path.join(OUT_DIR, "batch_output.jsonl")
OUTPUT_XLSX = os.path.join(OUT_DIR, "apps_with_classification.xlsx")
LATEST_CLASSIFIED_XLSX = os.path.join(OUT_DIR, "latest_classified.xlsx")
BATCH_STATUS_FILE = os.path.join(BACKEND_ROOT, "batch_status.json")

# ---------- Model / Batch ----------
MODEL = "gpt-5-mini"
TEMPERATURE = 0
COMPLETION_WINDOW = "24h"   # Batch API cost tier
CHUNK_SIZE = 200            # apps per request (prompt sent once per chunk)
MAX_REQUESTS_PER_FILE = 130

# ---------- Input columns ----------
COL_ID = "id"
COL_PLATFORM = "platform"   # "iOS" or "Android"

# ---------- Networking / scraping ----------
REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 2
