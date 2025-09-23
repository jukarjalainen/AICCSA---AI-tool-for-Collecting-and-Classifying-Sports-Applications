import pandas as pd

# Load the Excel file to examine specific problematic rows
df = pd.read_excel("appsTableClearForAI.xlsx")

print("Column names in the Excel file:")
print(df.columns.tolist())
print(f"\nTotal rows: {len(df)}")

# Check what's in row index 8 that keeps getting skipped
problematic_indices = [8, 13, 18, 33, 43]

print("\nExamining problematic rows that are consistently left empty:")
print("=" * 60)

for idx in problematic_indices:
    if idx < len(df):
        row = df.iloc[idx]
        print(f"\nRow {idx}:")
        # Print first few columns to understand the structure
        for col in df.columns[:8]:
            val = row[col] if col in row.index else 'N/A'
            print(f"  {col}: {val}")
        print("  ---")