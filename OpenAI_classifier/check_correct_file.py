import pandas as pd

# Load the correct Excel file
df = pd.read_excel(r'c:\Koulu\Sport HCI\scraper\OpenAI_classifier\appsTableClearForAI.xlsx')
print(f'Total rows: {len(df)}')
print(f'Total columns: {len(df.columns)}')

# Check which ID columns are present
alt_id_cols = ['id', 'bundleId', 'bundle_id', 'appId', 'app_id', 'package', 'package_name', 'packageId']
present = [c for c in alt_id_cols if c in df.columns]
print(f'ID columns present from alt_id_cols: {present}')

# Check if App_ID is present
if 'App_ID' in df.columns:
    print('App_ID column is present but NOT in alt_id_cols search list!')
    print(f'App_ID null/nan count: {df["App_ID"].isna().sum()}')
else:
    print('App_ID column not found')

# Show what key column would be used
if present:
    key_col = present[0]
    print(f'\nUsing key column: {key_col}')
    print(f'Key column null/nan count: {df[key_col].isna().sum()}')
    print(f'Key column non-null count: {df[key_col].notna().sum()}')
    
    # Check problematic rows we identified earlier
    problematic_indices = [7, 12, 17, 32, 42]  # 0-based
    print(f'\nChecking problematic rows (0-based indices):')
    for idx in problematic_indices[:5]:
        if idx < len(df):
            key_val = df.iloc[idx][key_col]
            app_id_val = df.iloc[idx]["App_ID"] if "App_ID" in df.columns else "N/A"
            app_name = df.iloc[idx].get("App_Name", df.iloc[idx].get("title", "Unknown"))
            print(f'  Row {idx}: {key_col}={key_val}, App_ID={app_id_val}, Name={app_name}')
else:
    print('No ID columns found!')

# Show all column names
print(f'\nFirst 10 column names: {list(df.columns)[:10]}')
if 'App_ID' in df.columns:
    print(f'App_ID is at index: {list(df.columns).index("App_ID")}')