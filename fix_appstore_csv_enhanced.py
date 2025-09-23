#!/usr/bin/env python3
"""
Enhanced CSV Fixer for App Store Data
Fixes broken CSV structure caused by multi-line text in releaseNotes and other fields
"""

import csv
import re
import os
from pathlib import Path

def fix_appstore_csv(input_file, output_file=None, expected_cols=None):
    """
    Fix broken CSV structure in App Store scraped data
    
    Args:
        input_file: Path to the broken CSV file
        output_file: Path for the fixed CSV file (auto-generated if None)
        expected_cols: Expected number of columns (auto-detected from header if None)
    """
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return False
    
    if output_file is None:
        # Generate output filename
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_FIXED{input_path.suffix}"
    
    print(f"Fixing CSV: {input_file} -> {output_file}")
    
    fixed_rows = 0
    merged_lines = 0
    empty_rows_removed = 0
    
    with open(input_file, "r", encoding="utf-8", errors="ignore") as infile:
        # Read all lines first to analyze structure
        all_lines = list(csv.reader(infile))
    
    if not all_lines:
        print("Error: Empty file")
        return False
    
    # Detect expected columns from header
    header = all_lines[0]
    if expected_cols is None:
        expected_cols = len(header)
    
    print(f"Expected columns: {expected_cols}")
    print(f"Header columns: {len(header)}")
    print(f"Total rows to process: {len(all_lines)}")
    
    # Find releaseNotes column index for targeted fixing
    release_notes_idx = None
    try:
        release_notes_idx = header.index('releaseNotes')
        print(f"Found releaseNotes column at index: {release_notes_idx}")
    except ValueError:
        print("Warning: releaseNotes column not found in header")
    
    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
        
        # Write header
        writer.writerow(header)
        
        buffer = []
        i = 1  # Start from 1 to skip header
        
        while i < len(all_lines):
            row = all_lines[i]
            
            # Skip completely empty rows
            if not row or all(cell.strip() == '' for cell in row):
                empty_rows_removed += 1
                i += 1
                continue
            
            if not buffer:
                buffer = row[:]  # Start new buffer
            else:
                # Check if current row looks like a continuation
                if len(buffer) < expected_cols or is_continuation_row(row, expected_cols):
                    # Merge this row into buffer
                    if len(row) > 0:
                        # Append to the last non-empty field in buffer (likely releaseNotes)
                        last_field_idx = find_last_non_empty_field(buffer)
                        if last_field_idx >= 0:
                            # Clean and merge the text
                            merged_text = clean_and_merge_text(buffer[last_field_idx], ' '.join(row))
                            buffer[last_field_idx] = merged_text
                        else:
                            # If no non-empty field, append to end
                            buffer.extend(row)
                        merged_lines += 1
                else:
                    # Current row looks like a new record
                    # Fix and write the buffered row
                    fixed_buffer = fix_row_structure(buffer, expected_cols, header)
                    writer.writerow(fixed_buffer)
                    fixed_rows += 1
                    
                    # Start new buffer with current row
                    buffer = row[:]
            
            i += 1
        
        # Write the last buffered row
        if buffer:
            fixed_buffer = fix_row_structure(buffer, expected_cols, header)
            writer.writerow(fixed_buffer)
            fixed_rows += 1
    
    print(f"\nFixing completed:")
    print(f"  - Fixed rows: {fixed_rows}")
    print(f"  - Merged continuation lines: {merged_lines}")
    print(f"  - Removed empty rows: {empty_rows_removed}")
    print(f"  - Output file: {output_file}")
    
    return True

def is_continuation_row(row, expected_cols):
    """Check if a row looks like a continuation of previous row"""
    if len(row) == 1 and row[0].strip():
        # Single field with text - likely continuation
        return True
    
    if len(row) < expected_cols // 2:
        # Much fewer fields than expected - likely continuation
        return True
    
    # Check if first few fields look like they should be numeric IDs but aren't
    if len(row) > 0:
        first_field = row[0].strip()
        if first_field and not (first_field.isdigit() or first_field.startswith('com.')):
            # First field doesn't look like an ID - likely continuation
            return True
    
    return False

def find_last_non_empty_field(buffer):
    """Find the index of the last non-empty field in buffer"""
    for i in range(len(buffer) - 1, -1, -1):
        if buffer[i].strip():
            return i
    return -1

def clean_and_merge_text(original, additional):
    """Clean and merge text fields"""
    # Remove extra whitespace and newlines
    original = re.sub(r'\s+', ' ', str(original).strip())
    additional = re.sub(r'\s+', ' ', str(additional).strip())
    
    if not original:
        return additional
    if not additional:
        return original
    
    # Merge with a space
    merged = f"{original} {additional}".strip()
    
    # Limit length to prevent overly long fields
    if len(merged) > 5000:
        merged = merged[:5000] + "..."
    
    return merged

def fix_row_structure(row, expected_cols, header):
    """Fix row structure to match expected columns"""
    # Pad with empty strings if too short
    while len(row) < expected_cols:
        row.append('')
    
    # Truncate if too long
    if len(row) > expected_cols:
        # Try to merge extra fields into the last text field
        if len(row) > expected_cols:
            # Find a text field to merge into (prefer releaseNotes, description, etc.)
            text_fields = ['releaseNotes', 'description', 'summary', 'descriptionHTML']
            merge_idx = None
            
            for field in text_fields:
                try:
                    merge_idx = header.index(field)
                    break
                except ValueError:
                    continue
            
            if merge_idx is None:
                # Fallback to last field
                merge_idx = expected_cols - 1
            
            # Merge extra fields into the chosen field
            extra_fields = row[expected_cols:]
            row[merge_idx] = clean_and_merge_text(row[merge_idx], ' '.join(extra_fields))
            row = row[:expected_cols]
    
    return row

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix broken CSV files from App Store scraping')
    parser.add_argument('input_file', help='Input CSV file to fix')
    parser.add_argument('--output', '-o', help='Output CSV file (auto-generated if not specified)')
    parser.add_argument('--columns', '-c', type=int, help='Expected number of columns (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    success = fix_appstore_csv(args.input_file, args.output, args.columns)
    
    if success:
        print("\nCSV fixing completed successfully!")
    else:
        print("\nCSV fixing failed!")
        exit(1)

if __name__ == "__main__":
    main()
