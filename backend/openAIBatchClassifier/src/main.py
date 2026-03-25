import os
from . import config
from .build_batch import validate_descriptions, build_batch_input
from .submit_batch import submit_and_wait
from .merge_results import merge_to_excel

def main():
    if not os.path.exists(config.DESCRIPTIONS_JSONL):
        raise FileNotFoundError(
            f"Missing {config.DESCRIPTIONS_JSONL}. Run Phase 1 first:\n"
            f"  python -m openAIBatchClassifier.src.scrape_store"
        )

    total, empties = validate_descriptions(strict=False)
    print(f"Descriptions found: {total}, empty: {empties}")

    build_batch_input()
    submit_and_wait()
    merge_to_excel()

if __name__ == "__main__":
    main()
