import os
import argparse
from . import config
from .status_tracker import (
    init_status,
    update_stage,
    mark_completed,
    mark_failed,
)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Run OpenAI batch classification for scraped app data."
    )
    parser.add_argument(
        "--input-file",
        required=True,
        help="Path to scraper output CSV/XLSX containing app identifiers and platform.",
    )
    parser.add_argument(
        "--model",
        default=config.MODEL,
        help="OpenAI model for chat completions (default: gpt-5-mini).",
    )
    parser.add_argument(
        "--api-key",
        default="",
        help="Optional OpenAI API key. If omitted, environment OPENAI_API_KEY is used.",
    )
    return parser.parse_args()

def main():
    args = _parse_args()
    from .build_batch import validate_descriptions, build_batch_input
    from .submit_batch import submit_and_wait
    from .merge_results import merge_to_csv
    from .scrape_store import run_scrape

    try:
        config.DATA_FILE = os.path.abspath(args.input_file)
        config.MODEL = args.model

        if args.api_key:
            os.environ["OPENAI_API_KEY"] = args.api_key

        if not os.path.exists(config.DATA_FILE):
            raise FileNotFoundError(f"Input file not found: {config.DATA_FILE}")

        print("[batch] scrape-descriptions")
        update_stage("scraping")
        run_scrape()

        total, empties = validate_descriptions(strict=False)
        print(f"Descriptions found: {total}, empty: {empties}")

        print("[batch] build-input")
        update_stage("chunking")
        batch_input_files = build_batch_input()

        init_status(config.DATA_FILE, config.MODEL, batch_input_files)
        print("[batch] submit-openai")
        update_stage("uploading")
        output_files = submit_and_wait(batch_input_files)

        print("[batch] merge-results")
        update_stage("merging")
        out_path = merge_to_csv(config.DATA_FILE, output_files)
        mark_completed(out_path)
        print(f"[batch] completed: {out_path}")
    except Exception as exc:
        mark_failed(str(exc))
        raise

if __name__ == "__main__":
    main()
