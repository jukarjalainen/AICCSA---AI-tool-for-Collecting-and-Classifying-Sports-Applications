import pandas as pd

# Check columns in new file
df_new = pd.read_excel(r'apps_with_classification_2026-31-03_1127.xlsx')
print("Columns in 1127 file:")
print(list(df_new.columns))
print(f"\nTotal columns: {len(df_new.columns)}")
print(f"Total rows: {len(df_new)}")

# Check for column variations
print("\n\nSearching for classification-related columns:")
for col in df_new.columns:
    if any(word in col.lower() for word in ['relevant', 'purpose', 'sport', 'type']):
        print(f"  - {col}")
