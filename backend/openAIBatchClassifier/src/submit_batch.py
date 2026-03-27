import time
import importlib
from . import config
from .status_tracker import update_batch, update_stage

def submit_and_wait(batch_input_files: list[str]):
    try:
        OpenAI = importlib.import_module("openai").OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Python package 'openai' is required. Install it in the active "
            "environment, e.g. 'python -m pip install openai', before running batch submission."
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

        # Some completed batches may publish file ids with a short delay.
        output_file_id = getattr(b, "output_file_id", None)
        error_file_id = getattr(b, "error_file_id", None)
        if not output_file_id:
            for _ in range(6):
                time.sleep(10)
                b = client.batches.retrieve(batch.id)
                output_file_id = getattr(b, "output_file_id", None)
                error_file_id = getattr(b, "error_file_id", None)
                update_batch(
                    idx,
                    status=b.status,
                    outputFileId=output_file_id,
                    errorFileId=error_file_id,
                )
                if output_file_id:
                    break

        # Download results
        if not output_file_id:
            error_output_path = None
            if error_file_id:
                error_output_path = f"{config.BATCH_OUTPUT_JSONL}errors_{idx}.jsonl"
                error_bytes = client.files.content(error_file_id).read()
                with open(error_output_path, "wb") as f:
                    f.write(error_bytes)

            update_batch(
                idx,
                status="completed_missing_output",
                outputFile=None,
                outputFileId=output_file_id,
                errorFileId=error_file_id,
                errorFile=error_output_path,
            )
            raise RuntimeError(
                "Batch completed but no output_file_id was returned. "
                f"batch_id={batch.id}, error_file_id={error_file_id}, "
                f"saved_error_file={error_output_path}"
            )

        out_bytes = client.files.content(output_file_id).read()
        output_path = f"{config.BATCH_OUTPUT_JSONL}{idx}"
        with open(output_path, "wb") as f:
            f.write(out_bytes)
        output_files.append(output_path)
        update_batch(
            idx,
            status="completed",
            outputFile=output_path,
            outputFileId=output_file_id,
            errorFileId=error_file_id,
        )
        print("Wrote results:", output_path)

    return output_files

if __name__ == "__main__":
    submit_and_wait([f"{config.BATCH_INPUT_JSONL}1"])
