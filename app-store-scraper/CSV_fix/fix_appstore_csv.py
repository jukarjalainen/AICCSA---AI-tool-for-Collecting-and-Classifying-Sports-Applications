import csv

input_file = "COMPLETE_appstore.csv"      # your scraped CSV
output_file = "COMPLETE_appstore_clean.csv"   # cleaned version

expected_cols = 85  # adjust to the number of columns your schema should have. The current file has 85 columns based on our analysis

print("Starting..")

with open(input_file, "r", encoding="utf-8", errors="ignore") as infile, \
     open(output_file, "w", newline="", encoding="utf-8") as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    buffer = []
    for row in reader:
        if not buffer:  
            buffer = row
        else:
            if len(buffer) < expected_cols:
                # merge spillover line into the last text column (releaseNotes likely)
                buffer[-1] = buffer[-1] + " " + " ".join(row)
            else:
                # row looks fine, write buffered row
                writer.writerow(buffer)
                buffer = row
    
    # write the last row
    if buffer:
        writer.writerow(buffer)

print("Cleaning done. Output written to", output_file)
