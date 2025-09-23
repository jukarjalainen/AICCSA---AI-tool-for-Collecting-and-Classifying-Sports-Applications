# OpenAI classifier

This folder contains tools and outputs for classifying app metadata via OpenAI. First target: main user group (Athlete, Support staff, Supporter, etc.). Next: app purpose and sport type.

## Script

- classify_user_groups.py — reads your Excel/CSV with store URLs, fetches descriptions (Apple/Google Play), and classifies the main user group via OpenAI.

## Defaults

- Cache: OpenAI_classifier/cache/descriptions/
- Output (XLSX): OpenAI_classifier/<input_basename>\_classified.xlsx
- Output (CSV): OpenAI_classifier/<input_basename>\_classified.csv
- Classification cache: OpenAI_classifier/cache/descriptions/classify_cache.jsonl

## Usage (examples)

- Debug one URL (render Google Play when needed):
  $env:OPENAI_API_KEY="<your_key>" ; python -X utf8 OpenAI_classifier/classify_user_groups.py --debug-url <store_url> --render

- Classify a workbook (write a new classified copy in this folder):
  $env:OPENAI_API_KEY="<your_key>" ; python -X utf8 OpenAI_classifier/classify_user_groups.py appsCombinedXLSX.xlsx --render --resume --rpm 60

## Environment

- OpenAI: set OPENAI_API_KEY

## Notes

- Unknowns are allowed; script returns the closest label or Other.
- Use --limit and --resume for safe partial runs.
- Descriptions are cached and classifications are cached by description hash to reduce API calls.
