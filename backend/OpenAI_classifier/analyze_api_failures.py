print("Checking which rows from 56-71 range are in the 'no API results' list:")

# The debug output showed these indices got no results: [64, 33, 68, 9, 43, 13, 18, 52, 54, 24]
no_results_indices = [64, 33, 68, 9, 43, 13, 18, 52, 54, 24]

# Convert to 1-based row numbers for easier reading
no_results_rows = [idx + 1 for idx in no_results_indices]

print(f"Rows that got no API results: {no_results_rows}")

# Check which of these are in the 56-71 range
range_56_71 = list(range(56, 72))
overlap = [row for row in no_results_rows if row in range_56_71]

print(f"Rows in 56-71 range that got no API results: {overlap}")

if overlap:
    print(f"\n{len(overlap)} out of 16 rows (56-71) are still failing, but due to API response issues, not description fetching")
else:
    print(f"\nNone of the rows 56-71 are failing due to API response issues")
    print("The description fetching issue for rows 56-71 appears to be resolved!")