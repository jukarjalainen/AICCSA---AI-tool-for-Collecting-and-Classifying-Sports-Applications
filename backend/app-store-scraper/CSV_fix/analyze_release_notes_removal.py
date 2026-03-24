import csv

def analyze_release_notes_removal(input_file):
    """
    Analyze what would happen if we remove the releaseNotes column (column 16)
    """
    print("Analyzing impact of removing releaseNotes column...")
    
    total_rows = 0
    rows_with_release_notes_newlines = 0
    rows_with_description_newlines = 0
    structurally_broken_rows = 0
    valid_rows = 0
    release_notes_col = 16  # releaseNotes column index
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        expected_cols = len(header)
        
        print(f"Original CSV has {expected_cols} columns")
        print(f"releaseNotes is column {release_notes_col}: '{header[release_notes_col]}'")
        
        row_num = 1
        for row in reader:
            row_num += 1
            total_rows += 1
            
            # Check if row is structurally broken
            if len(row) != expected_cols:
                structurally_broken_rows += 1
                continue
                
            # Check for newlines in releaseNotes
            if release_notes_col < len(row) and '\n' in str(row[release_notes_col]):
                rows_with_release_notes_newlines += 1
                
            # Check for newlines in description (col 4)
            if 4 < len(row) and '\n' in str(row[4]):
                rows_with_description_newlines += 1
                
            # Check if row would be valid after removing releaseNotes
            if len(row) == expected_cols:
                valid_rows += 1
    
    print(f"\n=== ANALYSIS RESULTS ===")
    print(f"Total rows analyzed: {total_rows}")
    print(f"Structurally broken rows (wrong column count): {structurally_broken_rows}")
    print(f"Valid rows (correct column count): {valid_rows}")
    print(f"Rows with newlines in releaseNotes: {rows_with_release_notes_newlines}")
    print(f"Rows with newlines in description: {rows_with_description_newlines}")
    
    print(f"\n=== IMPACT OF REMOVING releaseNotes COLUMN ===")
    print(f"✅ Would fix: {rows_with_release_notes_newlines} rows with releaseNotes newlines")
    print(f"❌ Would NOT fix: {rows_with_description_newlines} rows with description newlines")
    print(f"❌ Would NOT fix: {structurally_broken_rows} structurally broken rows")
    
    # Calculate what percentage of problems would be fixed
    total_problems = rows_with_release_notes_newlines + rows_with_description_newlines + structurally_broken_rows
    fixed_problems = rows_with_release_notes_newlines
    
    if total_problems > 0:
        fix_percentage = (fixed_problems / total_problems) * 100
        print(f"\n🎯 Removing releaseNotes would fix {fix_percentage:.1f}% of all problems")
    
    return {
        'total_rows': total_rows,
        'structurally_broken': structurally_broken_rows,
        'release_notes_issues': rows_with_release_notes_newlines,
        'description_issues': rows_with_description_newlines,
        'fix_percentage': fix_percentage if total_problems > 0 else 0
    }

def create_csv_without_release_notes(input_file, output_file):
    """
    Create a new CSV file without the releaseNotes column
    """
    print(f"\nCreating CSV without releaseNotes column...")
    
    rows_written = 0
    rows_skipped = 0
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            
            # Process header
            header = next(reader)
            new_header = header[:16] + header[17:]  # Remove column 16 (releaseNotes)
            writer.writerow(new_header)
            
            print(f"New CSV will have {len(new_header)} columns (removed: {header[16]})")
            
            # Process data rows
            for row in reader:
                if len(row) == len(header):  # Only process structurally valid rows
                    new_row = row[:16] + row[17:]  # Remove column 16
                    writer.writerow(new_row)
                    rows_written += 1
                else:
                    rows_skipped += 1
    
    print(f"✅ Wrote {rows_written} rows to {output_file}")
    print(f"⚠️ Skipped {rows_skipped} structurally broken rows")
    
    return rows_written, rows_skipped

if __name__ == "__main__":
    input_file = "COMPLETE_appstore.csv"
    output_file = "COMPLETE_appstore_no_release_notes.csv"
    
    # Analyze the impact
    results = analyze_release_notes_removal(input_file)
    
    # Ask user if they want to proceed
    print(f"\n" + "="*60)
    print(f"RECOMMENDATION:")
    if results['fix_percentage'] > 50:
        print(f"✅ Removing releaseNotes would fix {results['fix_percentage']:.1f}% of problems - RECOMMENDED")
    else:
        print(f"⚠️ Removing releaseNotes would only fix {results['fix_percentage']:.1f}% of problems - LIMITED BENEFIT")
    
    # For now, let's create the file to see the impact
    print(f"\nCreating test file to see the result...")
    create_csv_without_release_notes(input_file, output_file)
