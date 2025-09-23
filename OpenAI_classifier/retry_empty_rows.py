#!/usr/bin/env python3
import os
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import from the original script
import sys
sys.path.append('.')
from openAIclassify import (
    fetch_description, classify_descriptions_batch, normalize_sport_type, 
    normalize_purpose, EXCEL_CLASS_COLUMNS, FETCH_WORKERS, BATCH_GPT_SIZE,
    SLEEP_TIME, INPUT_FILE, OUTPUT_FILE
)

def _abs(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(os.path.dirname(__file__), path)

def find_empty_rows_for_retry():
    """Find rows that are not classified and don't have description_missing=True"""
    
    # Load the classified data
    try:
        df = pd.read_excel(_abs(OUTPUT_FILE))
    except FileNotFoundError:
        print(f"❌ Output file {OUTPUT_FILE} not found. Run main classification first.")
        return []
    
    empty_indices = []
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        
        # Check if not classified (Athlete column is NaN/empty)
        is_classified = not pd.isna(row.get('Athlete'))
        
        # Check if description is marked as missing (skip these as they won't work anyway)
        desc_missing = row.get('description_missing', False)
        
        # Include only rows that are not classified AND don't have missing descriptions
        if not is_classified and not desc_missing:
            empty_indices.append(idx)
    
    return empty_indices

def retry_classification_for_empty_rows():
    """Run classification only for empty rows that might succeed on retry"""
    
    # Find empty rows suitable for retry
    empty_indices = find_empty_rows_for_retry()
    
    if not empty_indices:
        print("✅ No empty rows found that are suitable for retry!")
        return
    
    print(f"🔄 Found {len(empty_indices)} empty rows to retry classification")
    print(f"Row indices to retry: {empty_indices[:10]}{'...' if len(empty_indices) > 10 else ''}")
    
    # Load the source data
    source_df = pd.read_excel(_abs(INPUT_FILE))
    output_df = pd.read_excel(_abs(OUTPUT_FILE))
    
    # Determine key column
    alt_id_cols = ['id', 'bundleId', 'bundle_id', 'appId', 'app_id', 'package', 'package_name', 'packageId']
    present = [c for c in alt_id_cols if c in source_df.columns]
    if not present:
        raise RuntimeError("No id-like column found")
    key_col = present[0]
    
    # Process in batches
    successful_retries = 0
    failed_retries = 0
    
    for start in range(0, len(empty_indices), BATCH_GPT_SIZE):
        batch_indices = empty_indices[start:start + BATCH_GPT_SIZE]
        batch_rows = source_df.loc[batch_indices]
        
        print(f"\n🔄 Retrying batch: indices {batch_indices}")

        # --- PARALLEL DESCRIPTION FETCH ---
        fetch_jobs = {}
        with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as executor:
            row_to_appid = {}
            for idx, row in batch_rows.iterrows():
                plat_val = row.get("Platform") if "Platform" in source_df.columns else None
                app_id = str(row[key_col])
                row_to_appid[idx] = app_id
                fetch_jobs[executor.submit(fetch_description, app_id, plat_val)] = idx

            descriptions = {}
            for future in as_completed(fetch_jobs):
                idx = fetch_jobs[future]
                try:
                    descriptions[idx] = future.result()
                except Exception as e:
                    print(f"❌ Failed fetching description for row {idx+1}: {e}")
                    descriptions[idx] = None

        # Handle descriptions
        cleaned = {}
        missing_descriptions = []
        
        for i, d in descriptions.items():
            if isinstance(d, str) and d.strip():
                original_app_id = str(source_df.loc[i, key_col])
                cleaned[i] = {"id": original_app_id, "description": d}
                print(f"✅ Row {i+1}: Got description for {original_app_id}")
            else:
                # Mark as missing in output
                output_df.at[i, "description_missing"] = True
                missing_descriptions.append(i)
                failed_retries += 1
                print(f"❌ Row {i+1}: Still missing description")
                
        if not cleaned:
            print(f"❌ No valid descriptions found in retry batch")
            continue

        # --- GPT BATCH CLASSIFICATION ---
        try:
            print(f"🤖 Sending {len(cleaned)} apps to OpenAI API...")
            batch_results = classify_descriptions_batch(cleaned)
            
            print(f"📥 API returned {len(batch_results)} results for {len(cleaned)} sent")
            
            if len(batch_results) < len(cleaned):
                sent_indices = set(cleaned.keys())
                returned_indices = set(batch_results.keys())
                missing_results = sent_indices - returned_indices
                print(f"⚠️ {len(missing_results)} apps got no API results: {list(missing_results)}")
                failed_retries += len(missing_results)
                
            # Apply results with duplicate handling
            processed_app_ids = set()
            for idx, result in batch_results.items():
                original_app_id = str(source_df.loc[idx, key_col])
                
                if original_app_id in processed_app_ids:
                    continue
                processed_app_ids.add(original_app_id)
                
                # Find all rows in current batch with this app ID
                matching_rows = [i for i in batch_indices if str(source_df.loc[i, key_col]) == original_app_id]
                
                for row_idx in matching_rows:
                    # Apply classification to output dataframe
                    output_df.at[row_idx, "Athlete"] = bool(result.get("athlete", False))
                    output_df.at[row_idx, "Support_staff"] = bool(result.get("support_staff", False))
                    output_df.at[row_idx, "Supporter"] = bool(result.get("supporter", False))
                    output_df.at[row_idx, "Governing_entity"] = bool(result.get("governing_entity", False))
                    output_df.at[row_idx, "Game"] = bool(result.get("game", False))
                    output_df.at[row_idx, "Sport_Type"] = normalize_sport_type(result.get("sport_type"))
                    output_df.at[row_idx, "Purpose"] = normalize_purpose(result.get("purpose"))
                    output_df.at[row_idx, "Not_relevant"] = bool(result.get("not_relevant", False))
                    
                    successful_retries += 1
                    print(f"✅ Row {row_idx+1}: Successfully classified {original_app_id}")

        except Exception as e:
            print(f"❌ GPT batch failed: {e}")
            failed_retries += len(cleaned)

        # Short pause between batches
        if start + BATCH_GPT_SIZE < len(empty_indices):
            time.sleep(1)

    # Save results
    try:
        output_df.to_excel(_abs(OUTPUT_FILE), index=False)
        print(f"\n🎉 Retry completed!")
        print(f"✅ Successfully classified: {successful_retries} rows")
        print(f"❌ Still failed: {failed_retries} rows")
        print(f"💾 Results saved to {OUTPUT_FILE}")
        
        # Show final stats
        total_classified = output_df['Athlete'].notna().sum()
        total_rows = len(output_df)
        success_rate = (total_classified / total_rows) * 100
        print(f"📊 Overall success rate: {total_classified}/{total_rows} ({success_rate:.1f}%)")
        
    except PermissionError:
        print(f"⚠️ Permission denied saving to {OUTPUT_FILE}. Results in memory only.")

if __name__ == "__main__":
    print("🔄 Second Pass Classification - Retry Empty Rows")
    print("=" * 50)
    retry_classification_for_empty_rows()