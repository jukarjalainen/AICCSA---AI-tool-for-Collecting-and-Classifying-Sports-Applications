import pandas as pd
import json

print("=" * 90)
print("ANALYZING 1127 RUN WITH CHUNK_SIZE = 100")
print("=" * 90)

# Load the latest file
df_1127 = pd.read_excel(r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_1127.xlsx')

# Find the relevant column names
relevant_col = "not_relevant" if "not_relevant" in df_1127.columns else "Is_relevant"
print(f"\nRunning analysis on 1127 file ({len(df_1127)} apps)")
print(f"Detected column for relevance: '{relevant_col}'")

# Check unclassified
def is_unclassified(row):
    return pd.isna(row[relevant_col]) or pd.isna(row["Purpose"]) or pd.isna(row["Sport_Type"])

unclass = df_1127[df_1127.apply(is_unclassified, axis=1)]
classified = len(df_1127) - len(unclass)

print(f"\nClassification Status (1127):")
print(f"  Classified:   {classified}/{len(df_1127)} ({100*classified/len(df_1127):.1f}%)")
print(f"  Unclassified: {len(unclass)}/{len(df_1127)} ({100*len(unclass)/len(df_1127):.1f}%)")

# Check if retry batch output exists and has data
print(f"\n{'─'*90}")
print("CHECKING RETRY FEATURE EXECUTION")
print(f"{'─'*90}")

try:
    with open(r'backend/openAIBatchClassifier/out/descriptions_retry.jsonl', 'r') as f:
        retry_desc_count = sum(1 for _ in f)
    print(f"\n✓ Retry descriptions file exists: {retry_desc_count} apps were prepared for retry")
except FileNotFoundError:
    print(f"\n✗ No retry descriptions file (retry may not have run)")

try:
    with open(r'backend/openAIBatchClassifier/out/batch_output.jsonl1', 'r') as f:
        lines = f.readlines()
    
    print(f"✓ Batch output file exists: {len(lines)} lines")
    
    # Check what's in the batch output
    classifications = []
    for line in lines[:3]:  # Look at first 3 lines
        try:
            obj = json.loads(line)
            content = obj["response"]["body"]["choices"][0]["message"]["content"]
            start = content.find('[')
            end = content.rfind(']')
            if start != -1 and end != -1:
                parsed = json.loads(content[start:end+1])
                if isinstance(parsed, list):
                    classifications.extend(parsed)
        except:
            pass
    
    # Get sample
    if classifications:
        sample = classifications[0]
        print(f"\nSample classification from batch output:")
        print(f"  App ID:      {sample.get('id')}")
        print(f"  not_relevant: {sample.get('not_relevant')}")
        print(f"  purpose:     {sample.get('purpose')}")
        print(f"  sport_type:  {sample.get('sport_type')}")
        
except FileNotFoundError:
    print(f"\n✗ No batch output file")

# Adjusted comparison
print(f"\n{'─'*90}")
print("ADJUSTED COMPARISON (accounting for 9 missing apps)")
print(f"{'─'*90}")

adjusted_apps = 841
adjusted_classified = classified + (9 * classified // len(df_1127))  # Rough estimate

print(f"\n0917: 726/841 = 86.3% (CHUNK_SIZE = 150)")
print(f"1127: {classified}/{len(df_1127)} = {100*classified/len(df_1127):.1f}% (CHUNK_SIZE = 100, {len(df_1127)} apps)")
print(f"      If 1127 had all 841 apps at same rate: ~{adjusted_classified}/841 = ~{100*adjusted_classified/841:.1f}%")

if 100*adjusted_classified/841 < 86.3:
    print(f"\n⚠️  UNEXPECTED: CHUNK_SIZE=100 should IMPROVE accuracy, but it got WORSE")
    print(f"    Possible causes:")
    print(f"    1. Retry feature didn't run or failed silently")
    print(f"    2. Merge logic has a bug with CHUNK_SIZE=100")
    print(f"    3. Batch API returned incomplete results for size 100")
else:
    print(f"\n✅ EXPECTED: CHUNK_SIZE=100 improved accuracy as predicted")
