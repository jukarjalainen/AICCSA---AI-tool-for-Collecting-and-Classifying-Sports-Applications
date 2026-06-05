import openpyxl
import pandas as pd

# Read the updated AppSchema
wb = openpyxl.load_workbook('AppsSchema.xlsx')
ws = wb.active

# Extract column headers
cols = []
for i in range(1, 50):
    val = ws.cell(1, i).value
    if val:
        cols.append(val)
    else:
        break

print("Updated AppSchema columns:")
for i, c in enumerate(cols, 1):
    print(f"{i}. {c}")
    
print(f"\nTotal columns: {len(cols)}")

# Check if 'not_relevant' is in the schema
if 'not_relevant' in cols:
    print("\n✅ 'not_relevant' is in schema")
elif 'is_relevant' in cols:
    print("\n❌ 'is_relevant' is in schema (should be 'not_relevant')")
else:
    print("\n❌ Neither 'not_relevant' nor 'is_relevant' found")
