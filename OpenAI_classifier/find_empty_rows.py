import pandas as pd

# Load the classified data
df = pd.read_excel('apps_classified.xlsx')

print("Finding empty rows in the first 210 rows:")
print("=" * 50)

empty_rows = []
classified_rows = []

for row_num in range(1, 211):  # 1-based row numbers 1-210
    idx = row_num - 1  # Convert to 0-based index
    if idx < len(df):
        row = df.iloc[idx]
        is_classified = not pd.isna(row['Athlete'])
        
        if is_classified:
            classified_rows.append(row_num)
        else:
            empty_rows.append(row_num)
            app_id = row['id']
            app_name = row['App_Name'] if 'App_Name' in row else 'N/A'
            desc_missing = row.get('description_missing', False)
            print(f"Row {row_num}: {app_id}")
            print(f"  Name: {app_name}")
            print(f"  Desc missing: {desc_missing}")
            print()

print(f"Summary:")
print(f"Classified: {len(classified_rows)}/210 rows")
print(f"Empty: {len(empty_rows)}/210 rows")
print(f"Empty row numbers: {empty_rows}")

# Save the empty row indices (0-based) for use in the classification script
empty_indices = [row - 1 for row in empty_rows]
print(f"Empty row indices (0-based): {empty_indices}")

# Write these to a file for the classification script to use
with open('empty_row_indices.txt', 'w') as f:
    f.write(','.join(map(str, empty_indices)))
    
print(f"Saved {len(empty_indices)} empty row indices to empty_row_indices.txt")