import csv
import time

input_file = "COMPLETE_appstore.csv"
output_file = "COMPLETE_appstore_clean.csv"
expected_cols = 85

start_time = time.time()
row_count = 0
merged_count = 0

print(f"Starting to process {input_file}...")
print("Progress will be shown every 1000 rows...")

with open(input_file, "r", encoding="utf-8", errors="ignore") as infile, \
     open(output_file, "w", newline="", encoding="utf-8") as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    buffer = []
    for row in reader:
        row_count += 1
        
        # Show progress every 1000 rows
        if row_count % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"Processed {row_count:,} rows in {elapsed:.1f}s (merged: {merged_count})")
        
        if not buffer:  
            buffer = row
        else:
            if len(buffer) < expected_cols:
                # merge spillover line into the last text column
                if buffer:  # Safety check
                    buffer[-1] = buffer[-1] + " " + " ".join(row)
                    merged_count += 1
            else:
                # row looks fine, write buffered row
                writer.writerow(buffer)
                buffer = row
    
    # write the last row
    if buffer:
        writer.writerow(buffer)

elapsed = time.time() - start_time
print(f"\nCompleted! Processed {row_count:,} rows in {elapsed:.1f}s")
print(f"Merged {merged_count:,} broken lines")
print(f"Output written to {output_file}")
