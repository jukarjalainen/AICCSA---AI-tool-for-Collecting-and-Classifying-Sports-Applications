import pandas as pd

# Load the data to check for duplicates in the first 20 rows
df = pd.read_excel('appsTableClearForAI.xlsx')
df_output = pd.read_excel('apps_classified.xlsx')

print("First 20 rows - checking for duplicate app IDs:")
first_20 = df.head(20)
print(f"Available columns: {list(df.columns)}")

id_counts = first_20['id'].value_counts()
duplicates = id_counts[id_counts > 1]

if len(duplicates) > 0:
    print(f"Found {len(duplicates)} duplicate app IDs in first 20 rows:")
    for app_id, count in duplicates.items():
        print(f"  {app_id}: {count} instances")
        
        # Show details of duplicate rows
        duplicate_rows = first_20[first_20['id'] == app_id][['id', 'Athlete', 'Support_staff', 'Supporter']]
        print(f"    Details:")
        for idx, row in duplicate_rows.iterrows():
            classification_status = "CLASSIFIED" if not pd.isna(row['Athlete']) else "NOT CLASSIFIED"
            print(f"      Row {idx}: status={classification_status}")
        print()
else:
    print("No duplicate app IDs found in first 20 rows")

print(f"Classification status for first 20 rows:")
for i in range(20):
    row = df_output.iloc[i]
    app_id = row['id']
    status = "CLASSIFIED" if not pd.isna(row['Athlete']) else "NOT CLASSIFIED"
    print(f"Row {i}: {app_id} - {status}")