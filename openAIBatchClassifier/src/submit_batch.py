import time
from openai import OpenAI
from . import config

def submit_and_wait():
    client = OpenAI()

    # Upload batch input
    inp = client.files.create(file=open(config.BATCH_INPUT_JSONL, "rb"), purpose="batch")

    # Create batch for /v1/chat/completions
    batch = client.batches.create(
        input_file_id=inp.id,
        endpoint="/v1/chat/completions",
        completion_window=config.COMPLETION_WINDOW,
    )
    print("Batch submitted:", batch.id)

    # Poll
    while True:
        b = client.batches.retrieve(batch.id)
        if b.status in ("completed", "failed", "cancelled", "expired"):
            print("Batch status:", b.status)
            if b.status != "completed":
                raise RuntimeError(f"Batch ended with status: {b.status}")
            break
        time.sleep(30)

    # Download results
    out_bytes = client.files.content(b.output_file_id).read()
    with open(config.BATCH_OUTPUT_JSONL, "wb") as f:
        f.write(out_bytes)
    print("Wrote results:", config.BATCH_OUTPUT_JSONL)

if __name__ == "__main__":
    submit_and_wait()
