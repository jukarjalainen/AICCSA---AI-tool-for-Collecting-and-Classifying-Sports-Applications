import pandas as pd

# Load the Excel file
df = pd.read_excel(r'c:\Koulu\Sport HCI\scraper\master_app_schema1.xlsx')
print(f'Total columns: {len(df.columns)}')

# Check which ID columns are present
alt_id_cols = ['id', 'bundleId', 'bundle_id', 'appId', 'app_id', 'package', 'package_name', 'packageId']
present = [c for c in alt_id_cols if c in df.columns]
print(f'ID columns present from alt_id_cols: {present}')

# Check if App_ID is present (it's not in the search list)
if 'App_ID' in df.columns:
    print('App_ID column is present but NOT in alt_id_cols search list!')
    # Show App_ID values for problematic rows
    print(f'App_ID null/nan count: {df["App_ID"].isna().sum()}')
    print(f'App_ID first 10 values: {df["App_ID"].head(10).tolist()}')
else:
    print('App_ID column not found')

# Show what key column would be used
if present:
    key_col = present[0]
    print(f'\nUsing key column: {key_col}')
    print(f'Key column null/nan count: {df[key_col].isna().sum()}')
    print(f'Key column first 10 values: {df[key_col].head(10).tolist()}')
    
    # Check if the key column has valid values for the problematic rows we identified
    problematic_indices = [7, 12, 17, 32, 42]  # These are 0-based indices (row 8-1, 13-1, etc.)
    print(f'\nProblematic rows (0-based indices {problematic_indices}):')
    for idx in problematic_indices[:5]:  # Check first 5
        if idx < len(df):
            print(f'  Row {idx}: {key_col}={df.iloc[idx][key_col]}, App_ID={df.iloc[idx]["App_ID"] if "App_ID" in df.columns else "N/A"}')
else:
    print('No ID columns found!')