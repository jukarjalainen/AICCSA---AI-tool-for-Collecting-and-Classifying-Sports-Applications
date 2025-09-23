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

def fix_csv_newlines(input_file, output_file):
    """
    Fix CSV by removing newlines from description and releaseNotes fields
    """
    print(f"Fixing newlines in {input_file}...")
    
    rows_processed = 0
    rows_fixed = 0
    description_fixes = 0
    release_notes_fixes = 0
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            
            # Process header
            header = next(reader)
            writer.writerow(header)
            
            print(f"CSV has {len(header)} columns")
            print(f"Target columns: description (4), releaseNotes (16)")
            
            # Process data rows
            for row in reader:
                rows_processed += 1
                
                if len(row) != len(header):
                    # Skip structurally broken rows for now
                    continue
                
                row_fixed = False
                
                # Fix description field (column 4)
                if len(row) > 4 and '\n' in str(row[4]):
                    original_desc = row[4]
                    row[4] = clean_text_field(row[4])
                    description_fixes += 1
                    row_fixed = True
                
                # Fix releaseNotes field (column 16)
                if len(row) > 16 and '\n' in str(row[16]):
                    original_notes = row[16]
                    row[16] = clean_text_field(row[16])
                    release_notes_fixes += 1
                    row_fixed = True
                
                if row_fixed:
                    rows_fixed += 1
                
                # Write the (possibly fixed) row
                writer.writerow(row)
                
                # Progress indicator
                if rows_processed % 5000 == 0:
                    print(f"  Processed {rows_processed} rows...")
    
    print(f"\n=== RESULTS ===")
    print(f"✅ Rows processed: {rows_processed}")
    print(f"🔧 Rows fixed: {rows_fixed}")
    print(f"📝 Description fields fixed: {description_fixes}")
    print(f"📋 ReleaseNotes fields fixed: {release_notes_fixes}")
    print(f"💾 Output saved to: {output_file}")
    
    return {
        'processed': rows_processed,
        'fixed': rows_fixed,
        'description_fixes': description_fixes,
        'release_notes_fixes': release_notes_fixes
    }

def analyze_fixed_csv(fixed_file):
    """
    Analyze the fixed CSV to verify it's clean
    """
    print(f"\nVerifying fixed CSV: {fixed_file}")
    
    total_rows = 0
    problem_rows = 0
    
    with open(fixed_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        expected_cols = len(header)
        
        for row in reader:
            total_rows += 1
            
            # Check for structural issues
            if len(row) != expected_cols:
                problem_rows += 1
                continue
            
            # Check for remaining newlines in key fields
            if len(row) > 4 and '\n' in str(row[4]):
                problem_rows += 1
                print(f"  Warning: Row {total_rows + 1} still has newlines in description")
                continue
                
            if len(row) > 16 and '\n' in str(row[16]):
                problem_rows += 1
                print(f"  Warning: Row {total_rows + 1} still has newlines in releaseNotes")
                continue
    
    print(f"\n=== VERIFICATION RESULTS ===")
    print(f"Total rows: {total_rows}")
    print(f"Problem rows: {problem_rows}")
    
    if problem_rows == 0:
        print("🎉 SUCCESS: No newline issues found in fixed CSV!")
    else:
        print(f"⚠️ WARNING: {problem_rows} rows still have issues")
    
    return problem_rows == 0

def handle_broken_rows(input_file, output_file):
    """
    Attempt to fix structurally broken rows by merging continuation lines
    """
    print(f"\nAttempting to fix structurally broken rows...")
    
    fixed_rows = 0
    skipped_rows = 0
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            
            # Process header
            header = next(reader)
            writer.writerow(header)
            expected_cols = len(header)
            
            buffer = []
            
            for row in reader:
                if len(row) == expected_cols:
                    # Complete row - write buffer if exists, then this row
                    if buffer:
                        # Try to merge buffer into a complete row
                        merged_row = merge_broken_rows(buffer, expected_cols)
                        if merged_row:
                            # Clean the merged row
                            if len(merged_row) > 4:
                                merged_row[4] = clean_text_field(merged_row[4])
                            if len(merged_row) > 16:
                                merged_row[16] = clean_text_field(merged_row[16])
                            writer.writerow(merged_row)
                            fixed_rows += 1
                        else:
                            skipped_rows += len(buffer)
                        buffer = []
                    
                    # Clean and write the current complete row
                    if len(row) > 4:
                        row[4] = clean_text_field(row[4])
                    if len(row) > 16:
                        row[16] = clean_text_field(row[16])
                    writer.writerow(row)
                else:
                    # Incomplete row - add to buffer
                    buffer.append(row)
            
            # Handle any remaining buffer
            if buffer:
                merged_row = merge_broken_rows(buffer, expected_cols)
                if merged_row:
                    if len(merged_row) > 4:
                        merged_row[4] = clean_text_field(merged_row[4])
                    if len(merged_row) > 16:
                        merged_row[16] = clean_text_field(merged_row[16])
                    writer.writerow(merged_row)
                    fixed_rows += 1
                else:
                    skipped_rows += len(buffer)
    
    print(f"Fixed {fixed_rows} broken rows, skipped {skipped_rows} unfixable fragments")
    return fixed_rows, skipped_rows

def merge_broken_rows(row_fragments, expected_cols):
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

if __name__ == "__main__":
    input_file = "COMPLETE_appstore.csv"
    clean_output = "COMPLETE_appstore_cleaned.csv"
    final_output = "COMPLETE_appstore_fixed.csv"
    
    print("=" * 60)
    print("CSV NEWLINE FIXER")
    print("=" * 60)
    
    # Step 1: Fix newlines in structurally valid rows
    print("\nSTEP 1: Fixing newlines in valid rows...")
    results = fix_csv_newlines(input_file, clean_output)
    
    # Step 2: Verify the clean version
    print("\nSTEP 2: Verifying cleaned CSV...")
    is_clean = analyze_fixed_csv(clean_output)
    
    # Step 3: Try to fix broken rows
    print("\nSTEP 3: Attempting to fix structurally broken rows...")
    fixed_count, skipped_count = handle_broken_rows(input_file, final_output)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"✅ Clean CSV (valid rows only): {clean_output}")
    print(f"🔧 Fixed CSV (includes repaired rows): {final_output}")
    print(f"📊 Description fixes: {results['description_fixes']}")
    print(f"📋 ReleaseNotes fixes: {results['release_notes_fixes']}")
    print(f"🛠️ Broken rows repaired: {fixed_count}")
    print(f"❌ Rows skipped (unfixable): {skipped_count}")
    print("=" * 60)
