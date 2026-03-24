import csv
import re

def clean_text_field(text):
    """
    Clean text field by removing/replacing problematic characters
    """
    if not text:
        return text
    
    # Convert to string if not already
    text = str(text)
    
    # Replace newlines with spaces
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def analyze_playstore_csv(input_file):
    """
    Analyze the PlayStore CSV to understand its structure and find issues
    """
    print(f"Analyzing PlayStore CSV: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        
        print(f"CSV has {len(header)} columns")
        print(f"Header: {header}")
        
        # Find description column
        description_col = None
        for i, col_name in enumerate(header):
            if 'description' in col_name.lower():
                description_col = i
                break
        
        if description_col is not None:
            print(f"Found description column at index {description_col}: '{header[description_col]}'")
        else:
            print("Warning: Could not find description column")
        
        return header, description_col

def fix_playstore_csv_newlines(input_file, output_file):
    """
    Fix PlayStore CSV by removing newlines from description field
    """
    print(f"Fixing newlines in {input_file}...")
    
    rows_processed = 0
    rows_fixed = 0
    description_fixes = 0
    wrong_column_count = 0
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            
            # Process header
            header = next(reader)
            writer.writerow(header)
            expected_cols = len(header)
            
            # Find description column
            description_col = None
            for i, col_name in enumerate(header):
                if 'description' in col_name.lower():
                    description_col = i
                    break
            
            print(f"CSV has {expected_cols} columns")
            print(f"Target column: description ({description_col})")
            
            # Process data rows
            for row in reader:
                rows_processed += 1
                
                # Check for wrong column count
                if len(row) != expected_cols:
                    wrong_column_count += 1
                    print(f"  Row {rows_processed + 1}: Wrong column count ({len(row)} vs {expected_cols})")
                    print(f"    First few fields: {row[:3] if len(row) >= 3 else row}")
                    continue
                
                row_fixed = False
                
                # Fix description field if found
                if description_col is not None and len(row) > description_col and '\n' in str(row[description_col]):
                    original_desc = row[description_col]
                    row[description_col] = clean_text_field(row[description_col])
                    description_fixes += 1
                    row_fixed = True
                
                if row_fixed:
                    rows_fixed += 1
                
                # Write the (possibly fixed) row
                writer.writerow(row)
                
                # Progress indicator
                if rows_processed % 1000 == 0:
                    print(f"  Processed {rows_processed} rows...")
    
    print(f"\n=== RESULTS ===")
    print(f"✅ Rows processed: {rows_processed}")
    print(f"🔧 Rows fixed: {rows_fixed}")
    print(f"📝 Description fields fixed: {description_fixes}")
    print(f"❌ Wrong column count: {wrong_column_count}")
    print(f"💾 Output saved to: {output_file}")
    
    return {
        'processed': rows_processed,
        'fixed': rows_fixed,
        'description_fixes': description_fixes,
        'wrong_column_count': wrong_column_count
    }

def analyze_fixed_playstore_csv(fixed_file):
    """
    Analyze the fixed CSV to verify it's clean
    """
    print(f"\nVerifying fixed CSV: {fixed_file}")
    
    total_rows = 0
    problem_rows = 0
    description_col = None
    
    with open(fixed_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        expected_cols = len(header)
        
        # Find description column
        for i, col_name in enumerate(header):
            if 'description' in col_name.lower():
                description_col = i
                break
        
        for row in reader:
            total_rows += 1
            
            # Check for structural issues
            if len(row) != expected_cols:
                problem_rows += 1
                continue
            
            # Check for remaining newlines in description field
            if description_col is not None and len(row) > description_col and '\n' in str(row[description_col]):
                problem_rows += 1
                print(f"  Warning: Row {total_rows + 1} still has newlines in description")
                continue
    
    print(f"\n=== VERIFICATION RESULTS ===")
    print(f"Total rows: {total_rows}")
    print(f"Problem rows: {problem_rows}")
    
    if problem_rows == 0:
        print("🎉 SUCCESS: No newline issues found in fixed CSV!")
    else:
        print(f"⚠️ WARNING: {problem_rows} rows still have issues")
    
    return problem_rows == 0

def handle_broken_playstore_rows(input_file, output_file):
    """
    Attempt to fix structurally broken rows by merging continuation lines
    """
    print(f"\nAttempting to fix structurally broken rows...")
    
    fixed_rows = 0
    skipped_rows = 0
    description_col = None
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            
            # Process header
            header = next(reader)
            writer.writerow(header)
            expected_cols = len(header)
            
            # Find description column
            for i, col_name in enumerate(header):
                if 'description' in col_name.lower():
                    description_col = i
                    break
            
            buffer = []
            
            for row in reader:
                if len(row) == expected_cols:
                    # Complete row - write buffer if exists, then this row
                    if buffer:
                        # Try to merge buffer into a complete row
                        merged_row = merge_broken_playstore_rows(buffer, expected_cols)
                        if merged_row:
                            # Clean the merged row
                            if description_col is not None and len(merged_row) > description_col:
                                merged_row[description_col] = clean_text_field(merged_row[description_col])
                            writer.writerow(merged_row)
                            fixed_rows += 1
                        else:
                            skipped_rows += len(buffer)
                        buffer = []
                    
                    # Clean and write the current complete row
                    if description_col is not None and len(row) > description_col:
                        row[description_col] = clean_text_field(row[description_col])
                    writer.writerow(row)
                else:
                    # Incomplete row - add to buffer
                    buffer.append(row)
            
            # Handle any remaining buffer
            if buffer:
                merged_row = merge_broken_playstore_rows(buffer, expected_cols)
                if merged_row:
                    if description_col is not None and len(merged_row) > description_col:
                        merged_row[description_col] = clean_text_field(merged_row[description_col])
                    writer.writerow(merged_row)
                    fixed_rows += 1
                else:
                    skipped_rows += len(buffer)
    
    print(f"Fixed {fixed_rows} broken rows, skipped {skipped_rows} unfixable fragments")
    return fixed_rows, skipped_rows

def merge_broken_playstore_rows(row_fragments, expected_cols):
    """
    Attempt to merge row fragments into a complete row
    """
    if not row_fragments:
        return None
    
    # Simple approach: concatenate all fragments
    merged = []
    for fragment in row_fragments:
        merged.extend(fragment)
    
    # If we have too many columns, it's probably not fixable
    if len(merged) > expected_cols * 2:
        return None
    
    # If we have fewer than expected, pad with empty strings
    while len(merged) < expected_cols:
        merged.append('')
    
    # If we have exactly the right number, return it
    if len(merged) == expected_cols:
        return merged
    
    # If we have too many, try to merge some fields
    if len(merged) > expected_cols:
        # Take the first expected_cols-1 fields, then merge the rest into the last field
        result = merged[:expected_cols-1]
        result.append(' '.join(str(x) for x in merged[expected_cols-1:]))
        return result
    
    return None

def looks_like_valid_playstore_start(row):
    """
    Check if a row looks like the start of a valid PlayStore app record
    """
    if not row or len(row) < 2:
        return False
    
    # First column should be title (non-empty string)
    title = str(row[0]).strip()
    if not title or title.isdigit():
        return False
    
    # Should have reasonable length for app title
    if len(title) > 200:
        return False
    
    return True

if __name__ == "__main__":
    # Check for available CSV files
    import os
    possible_files = [
        "PlayStoreAppsCSV.csv",
        "PlayStoreAppsCSV",
        "PlayStoreApps.csv",
        "../global_sports_fitness_apps_comprehensive.csv",
        "../sports_fitness_apps_comprehensive.csv"
    ]
    
    input_file = None
    for file_path in possible_files:
        if os.path.exists(file_path):
            input_file = file_path
            break
    
    if input_file is None:
        print("❌ No CSV file found! Looking for:")
        for f in possible_files:
            print(f"  - {f}")
        exit(1)
    
    print(f"📁 Using CSV file: {input_file}")
    
    # Set output filenames based on input
    base_name = os.path.basename(input_file).replace('.csv', '')
    clean_output = f"{base_name}_cleaned.csv"
    final_output = f"{base_name}_fixed.csv"
    
    print("=" * 60)
    print("PLAYSTORE CSV NEWLINE FIXER")
    print("=" * 60)
    
    # Step 0: Analyze the CSV structure
    print("\nSTEP 0: Analyzing CSV structure...")
    try:
        header, desc_col = analyze_playstore_csv(input_file)
    except FileNotFoundError:
        print(f"❌ File {input_file} not found!")
        print("Please make sure the PlayStore CSV file is in this directory.")
        exit(1)
    
    # Step 1: Fix newlines in structurally valid rows
    print("\nSTEP 1: Fixing newlines in valid rows...")
    results = fix_playstore_csv_newlines(input_file, clean_output)
    
    # Step 2: Verify the clean version
    print("\nSTEP 2: Verifying cleaned CSV...")
    is_clean = analyze_fixed_playstore_csv(clean_output)
    
    # Step 3: Try to fix broken rows
    print("\nSTEP 3: Attempting to fix structurally broken rows...")
    fixed_count, skipped_count = handle_broken_playstore_rows(input_file, final_output)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"✅ Clean CSV (valid rows only): {clean_output}")
    print(f"🔧 Fixed CSV (includes repaired rows): {final_output}")
    print(f"📝 Description fixes: {results['description_fixes']}")
    print(f"❌ Wrong column count: {results['wrong_column_count']}")
    print(f"🛠️ Broken rows repaired: {fixed_count}")
    print(f"❌ Rows skipped (unfixable): {skipped_count}")
    print("=" * 60)
