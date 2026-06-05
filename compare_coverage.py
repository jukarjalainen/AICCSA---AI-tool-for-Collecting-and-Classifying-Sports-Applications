import pandas as pd

# Read the newly uploaded file
new_file = r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_1048.xlsx'
df_new = pd.read_excel(new_file)

# Check for unclassified (NaN in critical fields)
def is_unclassified(row):
    required_fields = ["not_relevant", "Purpose", "Sport_Type"]
    for field in required_fields:
        if pd.isna(row[field]):
            return True
    return False

unclass_new = df_new[df_new.apply(is_unclassified, axis=1)]
classified_new = len(df_new) - len(unclass_new)

print("=== NEW FILE (2026-31-03_1048.xlsx) ===")
print(f"Total rows: {len(df_new)}")
print(f"Classified: {classified_new} ({100*classified_new/len(df_new):.1f}%)")
print(f"Unclassified: {len(unclass_new)} ({100*len(unclass_new)/len(df_new):.1f}%)")
print()

print("=== EARLIER FILE (latest_classified.xlsx) ===")
print(f"Total rows: 841")
print(f"Classified: 726 (86.3%)")
print(f"Unclassified: 115 (13.7%)")
print()

if len(unclass_new) > 115:
    diff = len(unclass_new) - 115
    print(f"⚠️  REGRESSION: {diff} MORE unclassified rows in new file")
elif len(unclass_new) < 115:
    diff = 115 - len(unclass_new)
    print(f"✅ IMPROVEMENT: {diff} fewer unclassified rows in new file")
else:
    print(f"➡️  UNCHANGED: Same number of unclassified rows")

print(f"\nSample unclassified apps from new file (first 5):")
if len(unclass_new) > 0:
    print(unclass_new[["App_ID", "App_Name", "Is_relevant", "Purpose", "Sport_Type"]].head(5).to_string())
