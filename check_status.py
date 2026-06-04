import pandas as pd

df = pd.read_excel(r'backend/openAIBatchClassifier/out/latest_classified.xlsx')

# Check for unclassified (NaN in critical fields)
def is_unclassified(row):
    required_fields = ["not_relevant", "Purpose", "Sport_Type"]
    for field in required_fields:
        if pd.isna(row[field]):
            return True
    return False

unclass = df[df.apply(is_unclassified, axis=1)]
classified = len(df) - len(unclass)

print(f"Total rows: {len(df)}")
print(f"Classified: {classified} ({100*classified/len(df):.1f}%)")
print(f"Unclassified: {len(unclass)} ({100*len(unclass)/len(df):.1f}%)")

if len(unclass) > 0:
    print(f"\nSample unclassified apps (first 5):")
    print(unclass[["App_ID", "App_Name", "Is_relevant", "Purpose", "Sport_Type"]].head(5).to_string())
