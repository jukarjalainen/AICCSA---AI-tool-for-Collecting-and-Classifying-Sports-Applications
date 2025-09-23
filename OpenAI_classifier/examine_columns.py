import pandas as pd

# Load the Excel file
df = pd.read_excel(r'c:\Koulu\Sport HCI\scraper\master_app_schema1.xlsx')
print(f'Total columns: {len(df.columns)}')
print(f'All column names: {list(df.columns)}')

# Look for any ID-like columns
id_like = [col for col in df.columns if 'id' in col.lower() or 'app' in col.lower()]
print(f'\nID-like columns: {id_like}')

# Check the id column specifically
print(f'\nid column stats:')
print(f'  Total values: {len(df["id"])}')
print(f'  Null/NaN count: {df["id"].isna().sum()}')
print(f'  Non-null count: {df["id"].notna().sum()}')
print(f'  Unique values: {df["id"].nunique()}')

# Show first 20 values
print(f'\nFirst 20 id values:')
for i in range(min(20, len(df))):
    print(f'  Row {i}: id={df.iloc[i]["id"]}')