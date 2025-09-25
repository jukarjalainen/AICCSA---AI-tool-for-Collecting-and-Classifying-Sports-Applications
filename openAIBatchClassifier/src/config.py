import os

# Base paths (resolve relative to this package)
PKG_ROOT = os.path.dirname(os.path.dirname(__file__))  # .../openAIBatchClassifier
PROMPTS_DIR = os.path.join(PKG_ROOT, "prompts")
DATA_DIR = os.path.join(PKG_ROOT, "data")
OUT_DIR = os.path.join(PKG_ROOT, "out")

# ---------- Files ----------
DATA_XLSX = os.path.join(DATA_DIR, "apps.xlsx")
PROMPT_FILE = os.path.join(PROMPTS_DIR, "classifier_prompt.txt")
DESCRIPTIONS_JSONL = os.path.join(OUT_DIR, "descriptions.jsonl")
BATCH_INPUT_JSONL = os.path.join(OUT_DIR, "batch_input.jsonl")
BATCH_OUTPUT_JSONL = os.path.join(OUT_DIR, "batch_output.jsonl")
OUTPUT_XLSX = os.path.join(OUT_DIR, "apps_with_classification.xlsx")

# ---------- Model / Batch ----------
MODEL = "gpt-5-mini"
TEMPERATURE = 0
COMPLETION_WINDOW = "24h"   # Batch API cost tier
CHUNK_SIZE = 200            # apps per request (prompt sent once per chunk)

# ---------- Input columns ----------
COL_ID = "id"
COL_PLATFORM = "Platform"   # "iOS" or "Android"

# ---------- Networking / scraping ----------
REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 2
