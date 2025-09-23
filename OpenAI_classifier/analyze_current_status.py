import pandas as pd

# Load the classified data
df = pd.read_excel('apps_classified.xlsx')

print("Analyzing empty rows in the dataset:")
print("=" * 40)

total_rows = len(df)
classified_count = 0
desc_missing_count = 0
api_failed_count = 0

empty_rows = []

for idx in range(total_rows):
    row = df.iloc[idx]
    
    is_classified = not pd.isna(row.get('Athlete'))
    desc_missing = row.get('description_missing', False)
    
    if is_classified:
        classified_count += 1
    else:
        empty_rows.append(idx + 1)  # 1-based row number
        if desc_missing:
            desc_missing_count += 1
            print(f"Row {idx+1}: DESC_MISSING - {row.get('id', 'unknown')}")
        else:
            api_failed_count += 1
            print(f"Row {idx+1}: API_FAILED - {row.get('id', 'unknown')}")

print(f"\nSummary for entire dataset:")
print(f"Total rows: {total_rows}")
print(f"Successfully classified: {classified_count}")
print(f"Empty due to missing descriptions: {desc_missing_count}")
print(f"Empty due to API failures: {api_failed_count}")
print(f"Overall success rate: {(classified_count/total_rows)*100:.1f}%")

if api_failed_count > 0:
    print(f"\n✅ {api_failed_count} rows could potentially be retried (API failures)")
else:
    print(f"\n❌ All empty rows have missing descriptions - no retry possible")

# Check specifically the first 210 rows
print(f"\nFirst 210 rows analysis:")
first_210_classified = sum(1 for i in range(min(210, total_rows)) if not pd.isna(df.iloc[i].get('Athlete')))
print(f"Classified in first 210: {first_210_classified}/210 ({(first_210_classified/210)*100:.1f}%)")