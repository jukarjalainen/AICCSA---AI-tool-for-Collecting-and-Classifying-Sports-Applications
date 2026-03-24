#!/usr/bin/env python3
"""
Targeted CSV Fixer for releaseNotes column leakage
"""

import csv
import re

def fix_release_notes_leakage(input_file, output_file):
    """
    Fix CSV where releaseNotes column causes row structure breaks
    """
    
    print(f"Fixing releaseNotes leakage in: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        
        # Find releaseNotes column index
        try:
            release_notes_idx = header.index('releaseNotes')
            print(f"Found releaseNotes at column {release_notes_idx}")
        except ValueError:
            print("releaseNotes column not found!")
            return
        
        expected_cols = len(header)
        print(f"Expected columns: {expected_cols}")
        
        rows = list(reader)
        print(f"Total rows to process: {len(rows)}")
    
    # Process and fix rows
    fixed_rows = []
    i = 0
    merged_count = 0
    
    while i < len(rows):
        row = rows[i]
        
        # Check if this row has the right structure
        if len(row) >= expected_cols and looks_like_valid_start(row):
            # This looks like a proper app record
            current_row = row[:]
            
            # Check if releaseNotes field might continue on next rows
            if len(current_row) > release_notes_idx:
                # Look ahead for continuation lines
                j = i + 1
                while j < len(rows) and not looks_like_valid_start(rows[j]):
                    # This row looks like continuation of releaseNotes
                    continuation_text = ' '.join(rows[j])
                    current_row[release_notes_idx] += ' ' + continuation_text
                    merged_count += 1
                    j += 1
                
                # Ensure row has correct number of columns
                while len(current_row) < expected_cols:
                    current_row.append('')
                current_row = current_row[:expected_cols]
                
                fixed_rows.append(current_row)
                i = j  # Skip the merged rows
            else:
                fixed_rows.append(current_row)
                i += 1
        else:
            # This row doesn't look like a valid start - might be orphaned
            i += 1
    
    # Write fixed data
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(fixed_rows)
    
    print(f"Fixed {len(fixed_rows)} rows, merged {merged_count} continuation lines")
    print(f"Output: {output_file}")

def looks_like_valid_start(row):
    """
    Check if a row looks like the start of a valid app record
    """
    if not row:
        return False
    
    # First column should be numeric ID
    first_col = str(row[0]).strip()
    if first_col.isdigit() and len(first_col) > 5:  # App Store IDs are typically 9+ digits
        return True
    
    # Or might start with bundle ID
    if first_col.startswith('com.') or first_col.startswith('id'):
        return True
    
    return False

def analyze_problem_area(input_file, start_row=540, end_row=560):
    """
    Analyze the specific problem area around row 546
    """
    print(f"\nAnalyzing rows {start_row}-{end_row}:")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        rows = list(reader)
    
    for i in range(start_row-1, min(end_row, len(rows))):
        row = rows[i]
        print(f"Row {i+2}: {len(row)} cols - {row[0][:50] if row else 'EMPTY'}...")
        if len(row) > 0 and row[0] == '430807521':
            print(f"  *** Found ID 430807521 at row {i+2} ***")

if __name__ == "__main__":
    input_file = "COMPLETE_appstore.csv"
    output_file = "COMPLETE_appstore_FIXED_targeted.csv"
    
    # First analyze the problem area
    analyze_problem_area(input_file)
    
    # Then fix the file
    fix_release_notes_leakage(input_file, output_file)
