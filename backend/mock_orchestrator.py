#!/usr/bin/env python3
"""
Mock Backend Orchestrator for UI Testing

This script simulates the AICCSA backend behavior for testing the Flutter UI
without the full scraping and OpenAI pipeline. It outputs realistic progress
messages and creates a sample output CSV.

Usage:
    python mock_orchestrator.py --store=google_play --keywords="sports" --countries=US,UK --model=gpt-4

Generated files:
    backend/batch_status.json - Batch tracking status
    backend/output/final_classified_apps.csv - Sample classified apps
"""

import argparse
import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime


def create_sample_csv():
    """Create a sample classified apps CSV for testing results display."""
    output_dir = Path('backend/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / 'final_classified_apps.csv'
    
    # Sample header and data
    header = 'App_ID,Title,Description,Store,Rating,User_Group,Sport_Type,Purpose,Country'
    rows = [
        'com.nike.running,Nike Run Club,Running app,google_play,4.8,Adult,Running,Training,US',
        'com.strava.android,Strava,Social fitness app,google_play,4.5,Young Adult,General,Community,US',
        'com.fitbit.FitbitApp,Fitbit,Health tracking,google_play,4.6,Adult,General,Health,US',
        'com.mapMyFitness.myfitnesspro,MapMyFitness,Workout tracking,google_play,4.4,Adult,Multiple,Training,US',
        'com.runtastic.android,Runtastic,Running companion,google_play,4.3,Adult,Running,Training,US',
    ]
    
    with open(csv_path, 'w') as f:
        f.write(header + '\n')
        for row in rows:
            f.write(row + '\n')
    
    print(f"Created sample CSV at {csv_path}", file=sys.stderr)


def update_batch_status(batch_ids: list, status: str):
    """Update the batch status JSON file."""
    status_dir = Path('backend')
    status_dir.mkdir(parents=True, exist_ok=True)
    
    status_file = status_dir / 'batch_status.json'
    
    status_data = {
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'batches': batch_ids,
        'completed_batches': batch_ids if status == 'completed' else [],
    }
    
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"Updated batch status: {status}", file=sys.stderr)


def simulate_processing(store: str, keywords: str, countries: list, model: str):
    """Simulate the processing pipeline with realistic delays and output."""
    
    total_duration = 15  # Total simulation time in seconds
    stage_times = {
        'scraping': 3,
        'chunking': 2,
        'uploading': 2,
        'polling': 5,
        'merging': 2,
        'completed': 1,
    }
    
    batch_ids = [
        'batch_65c8afd3-d98c-4fdc-8b17-d8a9e2e0d4e1',
        'batch_72f3e1c9-a5b1-4d2f-9e8c-1a2b3c4d5e6f',
    ]
    
    try:
        # Stage 1: Scraping
        print('AICCSA Backend Orchestrator Started')
        print(f'Configuration: store={store}, keywords={keywords}, countries={countries}, model={model}')
        print('Stage: scraping')
        update_batch_status([], 'scraping')
        time.sleep(stage_times['scraping'])
        
        # Stage 2: Chunking
        print('Scraped 234 apps from multiple stores')
        print('Stage: chunking')
        update_batch_status([], 'chunking')
        time.sleep(stage_times['chunking'])
        
        # Stage 3: Uploading
        print('Created 2 JSONL files with 130 requests each')
        print('Stage: uploading')
        update_batch_status(batch_ids, 'uploading')
        print(f'Batch IDs: {", ".join(batch_ids)}')
        time.sleep(stage_times['uploading'])
        
        # Stage 4: Polling
        print('Stage: polling')
        update_batch_status(batch_ids, 'polling')
        print('Polling OpenAI for batch completion...')
        time.sleep(stage_times['polling'])
        
        # Stage 5: Merging
        print('All batches completed!')
        print('Stage: merging')
        update_batch_status(batch_ids, 'merging')
        print('Merging results into final CSV...')
        time.sleep(stage_times['merging'])
        
        # Create sample output
        create_sample_csv()
        
        # Stage 6: Completion
        print('Stage: completed')
        update_batch_status(batch_ids, 'completed')
        print('Processing pipeline completed successfully!')
        print('Output: backend/output/final_classified_apps.csv')
        
        return 0
        
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        update_batch_status(batch_ids, 'error')
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Mock AICCSA Backend Orchestrator for UI Testing'
    )
    parser.add_argument('--store', default='google_play',
                        help='Target store: google_play, app_store, or both')
    parser.add_argument('--keywords', default='sports',
                        help='Search keywords (comma-separated)')
    parser.add_argument('--countries', default='US',
                        help='Countries to scrape (comma-separated)')
    parser.add_argument('--collection', default=None,
                        help='App Store collection (optional)')
    parser.add_argument('--model', default='gpt-4',
                        help='LLM model to use for classification')
    
    args = parser.parse_args()
    
    # Parse countries
    countries = [c.strip() for c in args.countries.split(',')]
    
    # Run simulation
    exit_code = simulate_processing(
        store=args.store,
        keywords=args.keywords,
        countries=countries,
        model=args.model,
    )
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
