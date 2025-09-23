#!/usr/bin/env python3
"""
Detailed analysis of specific problematic rows
"""

import csv

def analyze_specific_row(input_file, target_id="430807521"):
    """
    Find and analyze the row with the specific ID
    """
    print(f"Looking for app ID: {target_id}")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        
        # Find releaseNotes column
        try:
            release_notes_idx = header.index('releaseNotes')
            print(f"releaseNotes column index: {release_notes_idx}")
        except ValueError:
            print("releaseNotes column not found")
            return
        
        row_num = 1  # Start from 1 (header is 0)
        for row in reader:
            row_num += 1
            
            # Check if this row contains our target ID anywhere
            if target_id in str(row):
                print(f"\nFound '{target_id}' in row {row_num}")
                print(f"Row length: {len(row)} columns")
                print(f"Expected: {len(header)} columns")
                
                # Show first few columns
                print("\nFirst 5 columns:")
                for i, cell in enumerate(row[:5]):
                    col_name = header[i] if i < len(header) else f"EXTRA_{i}"
                    print(f"  {i}: {col_name} = '{cell[:100]}{'...' if len(cell) > 100 else ''}'")
                
                # Show releaseNotes column specifically
                if len(row) > release_notes_idx:
                    release_content = row[release_notes_idx]
                    print(f"\nreleaseNotes content (first 200 chars):")
                    print(f"'{release_content[:200]}{'...' if len(release_content) > 200 else ''}'")
                    
                    # Check for newlines in releaseNotes
                    if '\n' in release_content:
                        print("*** FOUND NEWLINES IN RELEASEOTES - THIS IS THE PROBLEM! ***")
                        lines = release_content.split('\n')
                        print(f"releaseNotes split into {len(lines)} lines:")
                        for i, line in enumerate(lines[:5]):  # Show first 5 lines
                            print(f"  Line {i+1}: '{line[:50]}{'...' if len(line) > 50 else ''}'")
                
                # Show columns around releaseNotes
                print(f"\nColumns around releaseNotes (index {release_notes_idx}):")
                for i in range(max(0, release_notes_idx-2), min(len(row), release_notes_idx+3)):
                    col_name = header[i] if i < len(header) else f"EXTRA_{i}"
                    cell_content = row[i] if i < len(row) else "MISSING"
                    print(f"  {i}: {col_name} = '{str(cell_content)[:50]}{'...' if len(str(cell_content)) > 50 else ''}'")
                
                break
        else:
            print(f"ID '{target_id}' not found in the file")

def find_problematic_rows(input_file, start_row=1000, end_row=2000):
    """
    Find rows that have newlines in text fields or wrong column count
    """
    print(f"Scanning rows {start_row}-{end_row} for issues...")
    
    problematic_rows = []
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        expected_cols = len(header)
        
        row_num = 1
        for row in reader:
            row_num += 1
            
            # Skip rows outside our range
            if row_num < start_row:
                continue
            if row_num > end_row:
                break
                
            # Check for wrong column count
            if len(row) != expected_cols:
                problematic_rows.append({
                    'row': row_num,
                    'issue': f'Wrong column count: {len(row)} (expected {expected_cols})',
                    'first_id': row[0] if row else 'NO_ID'
                })
                continue
                
            # Check each cell for newlines
            for i, cell in enumerate(row):
                if '\n' in str(cell):
                    col_name = header[i] if i < len(header) else f"EXTRA_{i}"
                    problematic_rows.append({
                        'row': row_num,
                        'issue': f'Newlines in {col_name} (col {i})',
                        'first_id': row[0] if row else 'NO_ID'
                    })
                    break  # One problem per row is enough
    
    print(f"\nFound {len(problematic_rows)} problematic rows:")
    for prob in problematic_rows:
        print(f"  Row {prob['row']}: {prob['issue']} - ID: {prob['first_id']}")
    
    return problematic_rows

if __name__ == "__main__":
    input_file = "COMPLETE_appstore.csv"
    
    # Check rows 1000-2000 as requested
    print("Starting analysis of rows 1000-2000...")
    problems = find_problematic_rows(input_file, start_row=1000, end_row=2000)
