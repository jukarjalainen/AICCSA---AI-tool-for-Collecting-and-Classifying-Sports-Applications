import csv

def count_rows_in_csv(filename):
    """Count the number of data rows in a CSV file (excluding header)"""
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            count = sum(1 for row in reader)
        return count
    except FileNotFoundError:
        return None

def analyze_data_loss():
    """Analyze how many apps were lost during cleaning"""
    
    original_file = "COMPLETE_appstore.csv"
    cleaned_file = "COMPLETE_appstore_cleaned.csv"
    
    print("=" * 50)
    print("DATA LOSS ANALYSIS")
    print("=" * 50)
    
    # Count rows in original file
    original_count = count_rows_in_csv(original_file)
    if original_count is None:
        print(f"❌ Could not read {original_file}")
        return
    
    # Count rows in cleaned file
    cleaned_count = count_rows_in_csv(cleaned_file)
    if cleaned_count is None:
        print(f"❌ Could not read {cleaned_file}")
        return
    
    # Calculate loss
    apps_lost = original_count - cleaned_count
    loss_percentage = (apps_lost / original_count) * 100 if original_count > 0 else 0
    
    print(f"📊 Original file: {original_count:,} apps")
    print(f"✅ Cleaned file: {cleaned_count:,} apps")
    print(f"❌ Apps lost: {apps_lost:,} apps")
    print(f"📉 Loss percentage: {loss_percentage:.2f}%")
    print(f"✅ Data retained: {100 - loss_percentage:.2f}%")
    
    print(f"\n" + "=" * 50)
    print("SUMMARY:")
    if loss_percentage < 5:
        print(f"🎉 EXCELLENT: Only {loss_percentage:.2f}% data loss")
    elif loss_percentage < 10:
        print(f"✅ GOOD: {loss_percentage:.2f}% data loss is acceptable")
    else:
        print(f"⚠️ HIGH: {loss_percentage:.2f}% data loss - consider investigation")
    
    print(f"You have {cleaned_count:,} clean, usable app records")
    print("=" * 50)
    
    return {
        'original': original_count,
        'cleaned': cleaned_count,
        'lost': apps_lost,
        'loss_percentage': loss_percentage
    }

if __name__ == "__main__":
    analyze_data_loss()
