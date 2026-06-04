import pandas as pd

df_1127 = pd.read_excel(r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_1127.xlsx')

# Find unclassified rows
def is_unclassified(row):
    return pd.isna(row['not_relevant']) or pd.isna(row['Purpose']) or pd.isna(row['Sport_Type'])

unclass_rows = df_1127[df_1127.apply(is_unclassified, axis=1)]

print(f"Apps with NaN in classification fields: {len(unclass_rows)}")
print(f"Sample unclassified apps (first 5):")
print(unclass_rows[['App_ID', 'App_Name', 'not_relevant', 'Purpose', 'Sport_Type']].head(5).to_string())

# Check retry descriptions to see what SHOULD have been processed
print(f"\n{'─'*90}")
print("RETRY FEATURE STATUS")
print(f"{'─'*90}")

try:
    with open(r'backend/openAIBatchClassifier/out/descriptions_retry.jsonl', 'r') as f:
        retry_count = sum(1 for _ in f)
    print(f"Retry descriptions prepared: {retry_count}")
    if retry_count == 0:
        print(f"\n⚠️  Retry feature found 0 unclassified apps (but there are {len(unclass_rows)} NaN rows!)")
        print(f"    This suggests a BUG in the unclassified detection logic.")
except Exception as e:
    print(f"Error reading retry descriptions: {e}")
