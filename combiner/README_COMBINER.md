# App Store and Play Store Data Combiner

## Overview

This system provides two Python programs to combine App Store and Play Store data according to your AppsSchema specification:

1. **`combine_app_stores_advanced.py`** - Full-featured combiner with deduplication
2. **`combine_tables.py`** - Simple combiner for basic combination

## Features

### Advanced Combiner (`combine_app_stores_advanced.py`)

✅ **Smart Duplicate Detection**: Removes duplicates based on:

- App ID (for apps available on both platforms)
- Title + Developer combination

✅ **Platform-Specific Fields**: Handles fields like:

- `score_appStore` and `score_playStore`
- `reviews_appStore` and `reviews_playStore`
- `price_appStore` and `price_playStore`

✅ **Calculated Fields**:

- `score_average` (when app is on both platforms)
- `reviews_total` (sum of both platforms)
- `availableOnBothPlatforms` (boolean flag)

✅ **Multiple Output Formats**:

- Schema-compliant CSV (semicolon-separated)
- Simple CSV (comma-separated)
- JSON format

✅ **Robust Error Handling**: Handles CSV parsing issues gracefully

## Usage

### Quick Start

```bash
# Run the advanced combiner (recommended)
& "C:/Koulu/Sport HCI/scraper/.venv/Scripts/python.exe" combine_app_stores_advanced.py

# Run the simple combiner
& "C:/Koulu/Sport HCI/scraper/.venv/Scripts/python.exe" combine_tables.py

# Alternative: Activate virtual environment first, then run normally
.\.venv\Scripts\Activate.ps1
python combine_app_stores_advanced.py
```

### Advanced Usage

```bash
# Specify custom file patterns
& "C:/Koulu/Sport HCI/scraper/.venv/Scripts/python.exe" combine_app_stores_advanced.py \
  --app-store-pattern "my_appstore_*.csv" \
  --play-store-pattern "my_playstore_*.csv" \
  --output-prefix "MY_COMBINED_apps"

# Use specific files
& "C:/Koulu/Sport HCI/scraper/.venv/Scripts/python.exe" combine_app_stores_advanced.py \
  --app-store-file "specific_appstore.csv" \
  --play-store-file "specific_playstore.csv"

# Mix specific file with pattern
& "C:/Koulu/Sport HCI/scraper/.venv/Scripts/python.exe" combine_app_stores_advanced.py \
  --app-store-file "specific_appstore.csv" \
  --play-store-pattern "COMPLETE_playstore_*.csv"
```

### Programmatic Usage

```python
from combine_app_stores_advanced import AppStoreCombiner

# Initialize combiner
combiner = AppStoreCombiner()

# Run combination
combined_data = combiner.run_combination()

# Access the DataFrame
print(f"Combined {len(combined_data)} apps")
```

## Input Requirements

The combiner expects these files in the current directory:

- `COMPLETE_appstore_*.csv` - Apple App Store data
- `COMPLETE_playstore_*.csv` - Google Play Store data
- `AppsSchema.csv` - Target schema definition

## Output Files

The advanced combiner creates three files:

1. **`COMBINED_apps_[timestamp].csv`** - Schema-compliant CSV with semicolons
2. **`COMBINED_apps_[timestamp]_simple.csv`** - Standard CSV with commas
3. **`COMBINED_apps_[timestamp].json`** - JSON format

## Schema Mapping

### Shared Fields

- `App_Name` ← `title`
- `developer` ← `developer`
- `description` ← `description`
- `icon` ← `icon`
- `url` ← `url`
- `free` ← `free`
- `currency` ← `currency`
- `released` ← `released`
- `updated` ← `updated`
- `version` ← `version`

### Platform-Specific Fields

**Apple App Store**:

- `score_appStore` ← `score`
- `reviews_appStore` ← `reviews`
- `genres_appStore` ← `genres`
- `primaryGenre_appStore` ← `primaryGenre`
- `Platform_Technology` = "iOS"
- `store` = "Apple App Store"

**Google Play Store**:

- `score_playStore` ← `score`
- `reviews_playStore` ← `reviews`
- `genre_playStore` ← `genre`
- `categories` ← `categories`
- `Platform_Technology` = "Android"
- `store` = "Google Play Store"

## Duplicate Detection Logic

The combiner finds duplicates using this priority:

1. **Same App ID** - Apps with identical `appId` or `id` fields
2. **Same Title + Developer** - Apps with identical normalized title and developer names

When duplicates are found:

- Platform-specific fields are preserved separately
- Shared fields use the first non-null value
- Cross-platform flags are set (`availableOnBothPlatforms = true`)
- Average scores and total reviews are calculated

## Results Summary

Recent combination results:

- **Total Apps**: 2,476 unique apps
- **Cross-Platform**: 303 apps available on both stores
- **iOS-Only**: 1,347 apps
- **Android-Only**: 1,129 apps
- **Duplicates Removed**: 123 duplicate entries

## Error Handling

The combiner handles:

- Malformed CSV files with inconsistent column counts
- Missing columns in source data
- Encoding issues (UTF-8 support)
- Empty or null values in key fields

## Dependencies

The combiner uses a Python virtual environment with required packages. The virtual environment is already set up with:

```bash
pip install pandas numpy
```

**To run the combiner, you must either:**

1. **Use the full virtual environment path** (recommended):

   ```bash
   & "C:/Koulu/Sport HCI/scraper/.venv/Scripts/python.exe" combine_app_stores_advanced.py
   ```

2. **Activate the virtual environment first**:

   ```bash
   .\.venv\Scripts\Activate.ps1
   python combine_app_stores_advanced.py
   ```

3. **If you get "pandas not found" errors**, you're not using the virtual environment.

## Troubleshooting

**"No files found" error**: Ensure you have the required CSV files in the directory
**CSV parsing errors**: The advanced combiner includes robust parsing to handle malformed CSV files
**Memory issues**: For very large datasets, consider processing in chunks

## Customization

To modify the schema mapping, edit the `app_store_mapping` and `play_store_mapping` dictionaries in `combine_app_stores_advanced.py`.

## License

This tool is provided as-is for research and data analysis purposes.
