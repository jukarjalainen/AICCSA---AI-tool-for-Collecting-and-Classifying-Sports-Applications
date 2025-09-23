import sys
import os
sys.path.append('.')

# Import the fetch_description function from openAIclassify.py
from openAIclassify import fetch_description
import pandas as pd

# Load the data to get the platform info for these apps
df = pd.read_excel('appsTableClearForAI.xlsx')

print("Testing description fetching for rows 56-61 (sample of problematic apps):")
print("=" * 70)

for row_num in range(56, 62):  # Test first 6 problematic rows
    idx = row_num - 1
    if idx < len(df):
        row = df.iloc[idx]
        app_id = row['id']
        app_name = row['App_Name'] if 'App_Name' in row else 'N/A'
        
        # Try to determine platform
        platform = None
        if 'Platform' in row:
            platform = row['Platform']
        elif 'platform' in row:
            platform = row['platform']
        elif 'platform2' in row:
            platform = row['platform2']
        
        print(f"\nRow {row_num}: {app_id}")
        print(f"  Name: {app_name}")
        print(f"  Platform: {platform}")
        
        try:
            description = fetch_description(app_id, platform)
            if description and description.strip():
                print(f"  ✅ Description found (length: {len(description)})")
                print(f"  Preview: {description[:100]}...")
            else:
                print(f"  ❌ No description returned")
        except Exception as e:
            print(f"  ❌ Error fetching description: {e}")