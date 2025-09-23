import csv

def find_problematic_rows_simple(input_file):
    """
    Find the exact 9 rows that have structural issues for manual fixing
    """
    print(f"Finding problematic rows in original file: {input_file}")
    
    problematic_rows = []
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        expected_cols = len(header)
        
        print(f"Expected columns: {expected_cols}")
        print(f"Header: {header[:5]}...")
        
        row_num = 1
        for row in reader:
            row_num += 1
            
            # Check for wrong column count (the main issue)
            if len(row) != expected_cols:
                problematic_rows.append({
                    'row_number': row_num,
                    'actual_cols': len(row),
                    'expected_cols': expected_cols,
                    'title': row[0] if row else 'NO_TITLE',
                    'description_start': row[1][:100] if len(row) > 1 else 'NO_DESCRIPTION'
                })
                
                if len(problematic_rows) <= 10:  # Show details for first 10
                    print(f"\nRow {row_num}: {len(row)} columns (expected {expected_cols})")
                    print(f"  Title: {row[0] if row else 'MISSING'}")
                    print(f"  Description start: {row[1][:80] if len(row) > 1 else 'MISSING'}...")
    
    print(f"\n=== SUMMARY ===")
    print(f"Found {len(problematic_rows)} problematic rows")
    print(f"\nFor manual fixing, focus on these row numbers:")
    for prob in problematic_rows:
        print(f"  Row {prob['row_number']}: '{prob['title']}' ({prob['actual_cols']} cols)")
    
    return problematic_rows

def restore_original_and_analyze():
    """
    Use the original file and just identify problem rows for manual fixing
    """
    original_file = "PlayStoreAppsCSV.csv"  # Your original file
    
    print("=" * 60)
    print("MANUAL FIX HELPER - IDENTIFYING PROBLEM ROWS")
    print("=" * 60)
    
    try:
        problems = find_problematic_rows_simple(original_file)
        
        print(f"\n" + "=" * 60)
        print("RECOMMENDATION:")
        print(f"✅ Only {len(problems)} rows need fixing - manual is definitely better!")
        print(f"🔧 Open {original_file} in Excel or text editor")
        print(f"📝 Fix the newlines in the description column for these specific rows")
        print(f"💡 Tip: Replace newlines (\\n) with spaces in the description text")
        print("=" * 60)
        
        return problems
        
    except FileNotFoundError:
        print(f"❌ Could not find {original_file}")
        print("Please make sure the original CSV file is in this directory")
        return []

if __name__ == "__main__":
    restore_original_and_analyze()
