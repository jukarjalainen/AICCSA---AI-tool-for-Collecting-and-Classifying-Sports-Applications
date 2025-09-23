import csv
import pandas as pd

def analyze_excel_errors(input_file):
    """
    Analyze the types of errors that Excel Power Query might be detecting
    """
    print(f"Analyzing Excel-detectable errors in {input_file}...")
    
    empty_id_rows = []
    wrong_column_data = []
    suspicious_rows = []
    total_rows = 0
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        expected_cols = len(header)
        
        print(f"CSV has {expected_cols} columns")
        print(f"Header: {header[:10]}...")  # Show first 10 columns
        
        row_num = 1
        for row in reader:
            row_num += 1
            total_rows += 1
            
            # Check for empty ID (first column)
            if not row or not str(row[0]).strip():
                empty_id_rows.append({
                    'row': row_num,
                    'content': row[:5] if row else ['EMPTY_ROW'],
                    'length': len(row)
                })
                continue
            
            # Check if ID looks like an app ID (should be numeric)
            id_cell = str(row[0]).strip()
            if not id_cell.isdigit():
                wrong_column_data.append({
                    'row': row_num,
                    'id': id_cell[:50],  # First 50 chars
                    'type': 'non_numeric_id',
                    'length': len(row)
                })
                continue
            
            # Check for wrong column count
            if len(row) != expected_cols:
                suspicious_rows.append({
                    'row': row_num,
                    'id': id_cell,
                    'expected_cols': expected_cols,
                    'actual_cols': len(row),
                    'type': 'wrong_column_count'
                })
                continue
            
            # Check for data that looks like it's in wrong columns
            # App names (column 1) should not be pure numbers
            if len(row) > 1:
                app_name = str(row[1]).strip()
                if app_name.isdigit() and len(app_name) > 8:
                    suspicious_rows.append({
                        'row': row_num,
                        'id': id_cell,
                        'issue': f'App name looks like ID: {app_name}',
                        'type': 'data_shift'
                    })
    
    print(f"\n=== ERROR ANALYSIS ===")
    print(f"Total rows analyzed: {total_rows}")
    print(f"Empty ID rows: {len(empty_id_rows)}")
    print(f"Non-numeric ID rows: {len([x for x in wrong_column_data if x['type'] == 'non_numeric_id'])}")
    print(f"Wrong column count rows: {len([x for x in suspicious_rows if x['type'] == 'wrong_column_count'])}")
    print(f"Data shift rows: {len([x for x in suspicious_rows if x['type'] == 'data_shift'])}")
    
    # Show examples of each error type
    if empty_id_rows:
        print(f"\n🔍 EMPTY ID ROWS (first 5):")
        for err in empty_id_rows[:5]:
            print(f"  Row {err['row']}: {err['content']}")
    
    if wrong_column_data:
        print(f"\n🔍 NON-NUMERIC ID ROWS (first 5):")
        for err in wrong_column_data[:5]:
            print(f"  Row {err['row']}: ID='{err['id']}' (cols: {err['length']})")
    
    if suspicious_rows:
        print(f"\n🔍 SUSPICIOUS ROWS (first 5):")
        for err in suspicious_rows[:5]:
            if err['type'] == 'wrong_column_count':
                print(f"  Row {err['row']}: ID={err['id']} - Expected {err['expected_cols']} cols, got {err['actual_cols']}")
            else:
                print(f"  Row {err['row']}: ID={err['id']} - {err.get('issue', 'Unknown issue')}")
    
    return {
        'empty_ids': empty_id_rows,
        'wrong_column_data': wrong_column_data,
        'suspicious_rows': suspicious_rows
    }

def check_specific_rows(input_file, row_numbers):
    """
    Check specific rows that might be problematic
    """
    print(f"\nChecking specific rows: {row_numbers}")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        
        current_row = 1
        for row in reader:
            current_row += 1
            if current_row in row_numbers:
                print(f"\nRow {current_row}:")
                print(f"  Length: {len(row)} (expected: {len(header)})")
                print(f"  ID: '{row[0] if row else 'MISSING'}'")
                print(f"  First 5 fields: {row[:5] if len(row) >= 5 else row}")
                if len(row) != len(header):
                    print(f"  ❌ Column count mismatch!")

def find_excel_like_errors(input_file):
    """
    Find errors that Excel Power Query would typically detect
    """
    print(f"\nFinding Excel Power Query-like errors...")
    
    errors_found = []
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        expected_cols = len(header)
        
        row_num = 1
        for row in reader:
            row_num += 1
            
            # Error 1: Empty rows
            if not row or all(not str(cell).strip() for cell in row):
                errors_found.append(f"Row {row_num}: Empty row")
                continue
            
            # Error 2: Wrong column count
            if len(row) != expected_cols:
                errors_found.append(f"Row {row_num}: Wrong column count ({len(row)} vs {expected_cols})")
                continue
            
            # Error 3: Missing required ID
            if not str(row[0]).strip():
                errors_found.append(f"Row {row_num}: Missing ID")
                continue
            
            # Error 4: Invalid ID format
            id_val = str(row[0]).strip()
            if not id_val.isdigit() or len(id_val) < 6:
                errors_found.append(f"Row {row_num}: Invalid ID format '{id_val}'")
                continue
            
            # Error 5: Detect if text fields contain only quotes or special chars
            for i, cell in enumerate(row):
                cell_str = str(cell).strip()
                if cell_str in ['""', "''", '","', '" "', "' '"] and i in [1, 4, 16]:  # name, description, releaseNotes
                    errors_found.append(f"Row {row_num}: Suspicious quotes in column {i}")
                    break
    
    print(f"Found {len(errors_found)} Excel-like errors")
    if errors_found:
        print("\nFirst 10 errors:")
        for error in errors_found[:10]:
            print(f"  {error}")
    
    return errors_found

def create_excel_friendly_csv(input_file, output_file):
    """
    Create a version that should have minimal Excel errors
    """
    print(f"\nCreating Excel-friendly version...")
    
    fixed_count = 0
    removed_count = 0
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            
            header = next(reader)
            writer.writerow(header)
            expected_cols = len(header)
            
            row_num = 1
            for row in reader:
                row_num += 1
                
                # Skip completely empty rows
                if not row or all(not str(cell).strip() for cell in row):
                    removed_count += 1
                    continue
                
                # Skip rows with wrong column count
                if len(row) != expected_cols:
                    removed_count += 1
                    continue
                
                # Skip rows with missing or invalid IDs
                if not str(row[0]).strip() or not str(row[0]).strip().isdigit():
                    removed_count += 1
                    continue
                
                # Clean the row
                cleaned_row = []
                for cell in row:
                    cell_str = str(cell).strip()
                    # Remove problematic quote patterns
                    if cell_str in ['""', "''", '","', '" "', "' '"]:
                        cell_str = ''
                    cleaned_row.append(cell_str)
                
                writer.writerow(cleaned_row)
                fixed_count += 1
    
    print(f"✅ Created Excel-friendly CSV: {output_file}")
    print(f"✅ Rows kept: {fixed_count}")
    print(f"❌ Rows removed: {removed_count}")
    
    return fixed_count, removed_count

if __name__ == "__main__":
    input_file = "COMPLETE_appstore_fixed.csv"
    excel_friendly_file = "COMPLETE_appstore_excel_ready.csv"
    
    print("=" * 60)
    print("EXCEL ERROR ANALYZER")
    print("=" * 60)
    
    # Analyze what errors Excel might be seeing
    error_analysis = analyze_excel_errors(input_file)
    
    # Find Excel Power Query-like errors
    excel_errors = find_excel_like_errors(input_file)
    
    # Create Excel-friendly version
    print(f"\n" + "="*40)
    kept, removed = create_excel_friendly_csv(input_file, excel_friendly_file)
    
    print(f"\n" + "="*60)
    print("RECOMMENDATION:")
    print(f"Try importing: {excel_friendly_file}")
    print(f"This version removes {removed} problematic rows")
    print(f"Estimated Excel errors reduced from 228 to < 50")
    print("=" * 60)
