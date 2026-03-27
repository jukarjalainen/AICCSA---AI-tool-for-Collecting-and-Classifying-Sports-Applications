import time
import importlib
from . import config
from .status_tracker import update_batch, update_stage

def submit_and_wait(batch_input_files: list[str]):
    try:
        OpenAI = importlib.import_module("openai").OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Python package 'openai' is required. Install dependencies from "
            "backend/openAIBatchClassifier/requirements before running batch submission."
        ) from exc

    client = OpenAI()
    output_files = []

    for idx, input_file in enumerate(batch_input_files, start=1):
        print(f"Submitting batch input file: {input_file}")
        update_batch(idx, status="uploading")
        with open(input_file, "rb") as f:
            inp = client.files.create(file=f, purpose="batch")

        # Create batch for /v1/chat/completions
        batch = client.batches.create(
            input_file_id=inp.id,
            endpoint="/v1/chat/completions",
            completion_window=config.COMPLETION_WINDOW,
        )
        print("Batch submitted:", batch.id)
        update_batch(idx, batchId=batch.id, status="submitted")

        # Poll
        update_stage("polling")
        while True:
            b = client.batches.retrieve(batch.id)
            update_batch(idx, status=b.status)
            if b.status in ("completed", "failed", "cancelled", "expired"):
                print("Batch status:", b.status)
                if b.status != "completed":
                    raise RuntimeError(f"Batch ended with status: {b.status}")
                break
            time.sleep(30)

        # Download results
        out_bytes = client.files.content(b.output_file_id).read()
        output_path = f"{config.BATCH_OUTPUT_JSONL}{idx}"
        with open(output_path, "wb") as f:
            f.write(out_bytes)
        output_files.append(output_path)
        update_batch(idx, status="completed", outputFile=output_path)
        print("Wrote results:", output_path)

    return output_files

if __name__ == "__main__":
    submit_and_wait([f"{config.BATCH_INPUT_JSONL}1"])
