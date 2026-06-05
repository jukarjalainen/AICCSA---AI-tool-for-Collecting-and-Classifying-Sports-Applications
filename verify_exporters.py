import re

# Read exporters.js to extract XLSX_SCHEMA_COLUMNS
with open('backend/modules/exporters.js', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Find XLSX_SCHEMA_COLUMNS array
match = re.search(r'const XLSX_SCHEMA_COLUMNS = \[(.*?)\];', content, re.DOTALL)
if match:
    cols_text = match.group(1)
    # Extract column names
    cols = re.findall(r'"([^"]+)"', cols_text)
    print(f"XLSX_SCHEMA_COLUMNS ({len(cols)} columns):")
    for i, col in enumerate(cols, 1):
        print(f"{i}. {col}")
    
    # Check for not_relevant
    if 'not_relevant' in cols:
        print("\n✅ 'not_relevant' found in exporters.js")
        print(f"✅ Position: {cols.index('not_relevant') + 1}")
    else:
        print("\n❌ 'not_relevant' NOT found")
        if 'Is_relevant' in cols:
            print("❌ Still using 'Is_relevant'")
            
# Also check buildSchemaXlsxRow for not_relevant
if 'not_relevant: app.not_relevant' in content:
    print("\n✅ buildSchemaXlsxRow uses 'not_relevant'")
elif 'Is_relevant: app.is_relevant' in content:
    print("\n❌ buildSchemaXlsxRow still uses 'is_relevant'")
