import pandas as pd

# Load the data to check rows 56-71 specifically
df_output = pd.read_excel('apps_classified.xlsx')

print("Checking rows 56-71 (originally reported as empty):")
print("=" * 60)

# Check rows 56-71 (note: these are 1-based row numbers, so we need indices 55-70)
for row_num in range(56, 72):  # 56 to 71 inclusive
    idx = row_num - 1  # Convert to 0-based index
    if idx < len(df_output):
        row = df_output.iloc[idx]
        app_id = row['id']
        app_name = row['App_Name'] if 'App_Name' in row else 'N/A'
        
        # Check if classified
        is_classified = not pd.isna(row['Athlete'])
        status = "CLASSIFIED" if is_classified else "NOT CLASSIFIED"
        
        # Check if description is missing
        desc_missing = row.get('description_missing', False)
        desc_status = "DESC_MISSING" if desc_missing else "DESC_OK"
        
        print(f"Row {row_num}: {app_id}")
        print(f"  Name: {app_name}")
        print(f"  Status: {status}")
        print(f"  Description: {desc_status}")
        
        # Show classification values if classified
        if is_classified:
            print(f"  Classifications: Athlete={row['Athlete']}, Support_staff={row['Support_staff']}, Supporter={row['Supporter']}")
            print(f"  Sport_Type={row['Sport_Type']}, Purpose={row['Purpose']}")
        print()
    else:
        print(f"Row {row_num}: INDEX OUT OF RANGE")

print("\nSummary:")
classified_count = 0
desc_missing_count = 0
for row_num in range(56, 72):
    idx = row_num - 1
    if idx < len(df_output):
        row = df_output.iloc[idx]
        if not pd.isna(row['Athlete']):
            classified_count += 1
        if row.get('description_missing', False):
            desc_missing_count += 1

print(f"Rows 56-71: {classified_count}/16 are classified")
print(f"Rows 56-71: {desc_missing_count}/16 have missing descriptions")