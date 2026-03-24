#!/usr/bin/env python3
"""
Analyze CSV file for structural issues
"""

import csv
import sys

def analyze_csv(filename):
    print(f"Analyzing: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader)
            print(f"Header columns: {len(header)}")
            
            rows = list(reader)
            print(f"Total rows: {len(rows)}")
            
            # Find problematic rows
            short_rows = []
            long_rows = []
            empty_rows = []
            
            for i, row in enumerate(rows):
                if not row or all(cell.strip() == '' for cell in row):
                    empty_rows.append(i)
                elif len(row) < len(header):
                    short_rows.append(i)
                elif len(row) > len(header):
                    long_rows.append(i)
            
            print(f"Rows with fewer columns than header: {len(short_rows)}")
            print(f"Rows with more columns than header: {len(long_rows)}")
            print(f"Empty rows: {len(empty_rows)}")
            
            if short_rows:
                print(f"First few short rows: {short_rows[:5]}")
            if long_rows:
                print(f"First few long rows: {long_rows[:5]}")
            
            # Check for releaseNotes column
            if 'releaseNotes' in header:
                release_idx = header.index('releaseNotes')
                print(f"Found releaseNotes column at index: {release_idx}")
            else:
                print("releaseNotes column not found")
                
            # Show some header columns
            print(f"First 10 header columns: {header[:10]}")
            
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_csv(sys.argv[1])
    else:
        # Default file
        analyze_csv("COMPLETE_appstore_sports_fitness_apps_2025-08-18T09-09-14-304Z.csv")
