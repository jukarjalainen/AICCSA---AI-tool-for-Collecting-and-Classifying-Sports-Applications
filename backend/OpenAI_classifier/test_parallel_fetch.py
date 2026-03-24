import sys
import os
sys.path.append('.')

from concurrent.futures import ThreadPoolExecutor, as_completed
from openAIclassify import fetch_description, FETCH_WORKERS
import pandas as pd
import time

# Load the data
df = pd.read_excel('appsTableClearForAI.xlsx')

print("Testing parallel description fetching for rows 56-71 (simulating batch processing):")
print("=" * 80)

# Test rows 56-71 with parallel processing like the actual script does
test_rows = list(range(55, 71))  # 0-based indices for rows 56-71

# Parallel fetch like in the real script
fetch_jobs = {}
start_time = time.time()

with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as executor:
    for idx in test_rows:
        if idx < len(df):
            row = df.iloc[idx]
            app_id = str(row['id'])
            
            # Get platform the same way the script does
            plat_val = row["Platform"] if "Platform" in df.columns else None
            
            fetch_jobs[executor.submit(fetch_description, app_id, plat_val)] = idx
    
    descriptions = {}
    successful = 0
    failed = 0
    
    for future in as_completed(fetch_jobs):
        idx = fetch_jobs[future]
        row_num = idx + 1  # Convert back to 1-based
        
        try:
            description = future.result()
            if isinstance(description, str) and description.strip():
                descriptions[idx] = description
                successful += 1
                print(f"✅ Row {row_num}: SUCCESS (length: {len(description)})")
            else:
                failed += 1
                print(f"❌ Row {row_num}: EMPTY DESCRIPTION")
        except Exception as e:
            failed += 1
            print(f"❌ Row {row_num}: ERROR - {e}")

end_time = time.time()
print(f"\nParallel fetch results:")
print(f"Time taken: {end_time - start_time:.2f} seconds")
print(f"Successful: {successful}/{len(test_rows)}")
print(f"Failed: {failed}/{len(test_rows)}")

if failed > 0:
    print(f"\n⚠️  {failed} apps failed description fetching in parallel mode")
    print("This explains why rows 56-71 were marked as DESC_MISSING")
else:
    print(f"\n✅ All apps successfully fetched descriptions in parallel mode")
    print("The DESC_MISSING issue might be intermittent or fixed")