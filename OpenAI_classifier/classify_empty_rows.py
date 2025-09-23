#!/usr/bin/env python3
import argparse
import json
import os
import pandas as pd
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

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

def classify_specific_rows(row_indices):
    """Classify only the specified row indices"""
    
    # Load the data
    source_df = pd.read_excel(_abs(INPUT_FILE))
    print(f"Loaded input {INPUT_FILE} with {len(source_df)} rows")
    
    # Determine key column (same logic as original script)
    alt_id_cols = ['id', 'bundleId', 'bundle_id', 'appId', 'app_id', 'package', 'package_name', 'packageId']
    present = [c for c in alt_id_cols if c in source_df.columns]
    if not present:
        raise RuntimeError("No id-like column found")
    key_col = present[0]
    print(f"Using key column: {key_col}")
    
    # Filter to only the specified indices
    work_indices = [idx for idx in row_indices if idx < len(source_df)]
    print(f"Processing {len(work_indices)} specific rows: {work_indices}")
    
    # Process in batches
    processed_count = 0
    for start in range(0, len(work_indices), BATCH_GPT_SIZE):
        batch_indices = work_indices[start:start + BATCH_GPT_SIZE]
        batch_rows = source_df.loc[batch_indices]
        print(f"\nProcessing batch: {batch_indices}")

        # --- PARALLEL DESCRIPTION FETCH ---
        fetch_jobs = {}
        with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as executor:
            row_to_appid = {}
            for idx, row in batch_rows.iterrows():
                plat_val = row["Platform"] if "Platform" in source_df.columns else None
                app_id = str(row[key_col])
                row_to_appid[idx] = app_id
                fetch_jobs[executor.submit(fetch_description, app_id, plat_val)] = idx

            descriptions = {}
            for future in as_completed(fetch_jobs):
                idx = fetch_jobs[future]
                try:
                    descriptions[idx] = future.result()
                except Exception as e:
                    print(f"❌ Failed fetching description for row {idx}: {e}")
                    descriptions[idx] = None

        # Handle rows with missing/empty descriptions
        cleaned = {}
        missing_descriptions = []
        app_id_to_rows = {}
        for i, d in descriptions.items():
            if isinstance(d, str) and d.strip():
                original_app_id = str(source_df.loc[i, key_col])
                cleaned[i] = {"id": original_app_id, "description": d}
                if original_app_id not in app_id_to_rows:
                    app_id_to_rows[original_app_id] = []
                app_id_to_rows[original_app_id].append(i)
                print(f"✅ Row {i+1}: Got description for {original_app_id} (length: {len(d)})")
            else:
                source_df.at[i, "description_missing"] = True
                missing_descriptions.append(i)
                print(f"❌ Row {i+1}: Missing description for {row_to_appid.get(i)}")
                
        if missing_descriptions:
            print(f"DEBUG: {len(missing_descriptions)} apps with missing descriptions (indices: {missing_descriptions})")
            
        descriptions = cleaned
        if not descriptions:
            print(f"DEBUG: No valid descriptions found in batch {batch_indices}")
            continue

        # --- GPT BATCH CLASSIFICATION ---
        try:
            print(f"DEBUG: Sending {len(descriptions)} apps to API from batch {batch_indices}")
            batch_results = classify_descriptions_batch(descriptions)
            
            print(f"DEBUG: API returned {len(batch_results)} results for {len(descriptions)} sent")
            if len(batch_results) < len(descriptions):
                sent_indices = set(descriptions.keys())
                returned_indices = set(batch_results.keys())
                missing_results = sent_indices - returned_indices
                print(f"DEBUG: {len(missing_results)} sent apps got no results (indices: {list(missing_results)})")
                
            # Apply results to all rows with the same app ID
            processed_app_ids = set()
            for idx, result in batch_results.items():
                original_app_id = str(source_df.loc[idx, key_col])
                
                if original_app_id in processed_app_ids:
                    continue
                processed_app_ids.add(original_app_id)
                
                # Find all rows in current batch with this app ID
                matching_rows = [i for i in batch_indices if str(source_df.loc[i, key_col]) == original_app_id]
                
                for row_idx in matching_rows:
                    # Apply classification
                    source_df.at[row_idx, "Athlete"] = bool(result.get("athlete")) if result.get("athlete") is not None else False
                    source_df.at[row_idx, "Support_staff"] = bool(result.get("support_staff")) if result.get("support_staff") is not None else False
                    source_df.at[row_idx, "Supporter"] = bool(result.get("supporter")) if result.get("supporter") is not None else False
                    source_df.at[row_idx, "Governing_entity"] = bool(result.get("governing_entity")) if result.get("governing_entity") is not None else False
                    source_df.at[row_idx, "Game"] = bool(result.get("game")) if result.get("game") is not None else False
                    source_df.at[row_idx, "Sport_Type"] = normalize_sport_type(result.get("sport_type"))
                    source_df.at[row_idx, "Purpose"] = normalize_purpose(result.get("purpose"))
                    source_df.at[row_idx, "Not_relevant"] = bool(result.get("not_relevant")) if result.get("not_relevant") is not None else False
                    
                    print(f"✅ Row {row_idx+1}: Classified {original_app_id}")

        except Exception as e:
            print(f"❌ GPT batch failed: {e}")

        processed_count += len(batch_indices)

    # Save results
    try:
        source_df.to_excel(_abs(OUTPUT_FILE), index=False)
        print(f"🎉 Classification completed! Saved results to {OUTPUT_FILE}")
    except PermissionError:
        print(f"⚠️ Permission denied saving to {OUTPUT_FILE}. Results in memory only.")

if __name__ == "__main__":
    # Read the empty row indices from file
    try:
        with open('empty_row_indices.txt', 'r') as f:
            indices_str = f.read().strip()
            empty_indices = [int(x) for x in indices_str.split(',') if x.strip()]
        
        print(f"Found {len(empty_indices)} empty row indices to process")
        print(f"Indices: {empty_indices[:10]}{'...' if len(empty_indices) > 10 else ''}")
        
        classify_specific_rows(empty_indices)
        
    except FileNotFoundError:
        print("❌ empty_row_indices.txt not found. Run find_empty_rows.py first.")
    except Exception as e:
        print(f"❌ Error: {e}")