#!/usr/bin/env python3
"""
Advanced App Store and Play Store Data Combiner
Combines data from both stores according to AppsSchema, handling duplicates and platform-specific fields.
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import re
import argparse

class AppStoreCombiner:
    def __init__(self):
        # Load schema from AppsSchema.csv (resolve robustly so script can run from any CWD)
        schema_candidates = []
        try:
            _here = os.path.dirname(os.path.abspath(__file__))
            # Parent dir versions
            schema_candidates.append(os.path.join(_here, '..', 'AppsSchema.csv'))
            schema_candidates.append(os.path.join(_here, '..', 'AppsSchemaCSV.csv'))
            # Local dir versions
            schema_candidates.append(os.path.join(_here, 'AppsSchema.csv'))
            schema_candidates.append(os.path.join(_here, 'AppsSchemaCSV.csv'))
        except Exception:
            pass
        # CWD fallbacks
        schema_candidates.append(os.path.join(os.getcwd(), 'AppsSchema.csv'))
        schema_candidates.append(os.path.join(os.getcwd(), 'AppsSchemaCSV.csv'))

        schema_path = next((p for p in schema_candidates if os.path.exists(p)), None)
        if not schema_path:
            raise FileNotFoundError(
                "AppsSchema.csv not found. Expected at one of: " + ", ".join(schema_candidates)
            )

        self.schema_df = pd.read_csv(schema_path, sep=';')
        self.target_columns = self.schema_df.columns.tolist()
        
        # Define platform-specific mappings
        self.app_store_mapping = {
            'id': 'id',
            'appId': 'appId_appStore', 
            'title': 'App_Name',
            'url': 'url',
            'description': 'description',
            'descriptionHTML': 'descriptionHTML',
            'summary': 'summary',
            'icon': 'icon',
            'headerImage': 'headerImage',
            'genres': 'genres_appStore',
            'genreIds': 'genreIds_appStore',
            'primaryGenre': 'primaryGenre_appStore',
            'primaryGenreId': 'primaryGenreId',
            'contentRating': 'contentRating',
            'released': 'released',
            'updated': 'updated',
            'version': 'version',
            'price': 'price_appStore',
            'currency': 'currency',
            'free': 'free',
            'developer': 'developer',
            'developerId': 'developerId',
            'developerUrl': 'developerUrl',
            'developerWebsite': 'developerWebsite',
            'developerLegalName': 'developerLegalName',
            'privacyPolicy': 'privacyPolicy',
            'score': 'score_appStore',
            'reviews': 'reviews_appStore',
            'platform': 'platform',
            'platforms': 'platforms',
            'availableOnBothPlatforms': 'availableOnBothPlatforms',
            'crossPlatformMethod': 'crossPlatformMethod',
            'crossPlatformAppIds': 'crossPlatformAppIds',
            'sourceMethod': 'sourceMethod',
            'sourceCollection': 'sourceCollection',
            'sourceCountry': 'sourceCountry',
            'searchQuery': 'searchQuery',
            'targetCategory': 'targetCategory',
            'developerInternalID': 'developerInternalID'
        }
        
        self.play_store_mapping = {
            'title': 'App_Name',
            'description': 'description',
            'descriptionHTML': 'descriptionHTML',
            'summary': 'summary',
            'icon': 'icon',
            'headerImage': 'headerImage',
            'genre': 'genre_playStore',
            'genreId': 'genreId_playStore',
            'categories': 'categories_playStore',
            'contentRating': 'contentRating',
            'released': 'released',
            'updated': 'updated',
            'version': 'version',
            'price': 'price_playStore',
            'currency': 'currency',
            'free': 'free',
            'developer': 'developer',
            'developerId': 'developerId',
            'developerEmail': 'developerEmail',
            'developerWebsite': 'developerWebsite',
            'developerAddress': 'developerAddress',
            'developerLegalName': 'developerLegalName',
            'developerLegalEmail': 'developerLegalEmail',
            'developerLegalAddress': 'developerLegalAddress',
            'developerLegalPhoneNumber': 'developerLegalPhoneNumber',
            'privacyPolicy': 'privacyPolicy',
            'score': 'score_playStore',
            'reviews': 'reviews',
            'ratings': 'ratings',
            'appId': 'appId_playStore',
            'url': 'url',
            'platform': 'platform',
            'platforms': 'platforms',
            'availableOnBothPlatforms': 'availableOnBothPlatforms',
            'crossPlatformMethod': 'crossPlatformMethod',
            'crossPlatformAppIds': 'crossPlatformAppIds',
            'sourceMethod': 'sourceMethod',
            'sourceCollection': 'sourceCollection',
            'sourceCountry': 'sourceCountry',
            'searchQuery': 'searchQuery',
            'targetCategory': 'targetCategory',
            'developerInternalID': 'developerInternalID'
        }

    def load_data_files(self, app_store_file="AppStoreAppsCSV.csv", play_store_file="PlayStoreAppsCSV.csv", 
                       app_store_pattern="AppStore*.csv", 
                       play_store_pattern="PlayStore*.csv"):
        """Load App Store and Play Store data files
        
        Args:
            app_store_file: Specific App Store file path (overrides pattern)
            play_store_file: Specific Play Store file path (overrides pattern)
            app_store_pattern: Pattern for App Store files (used if app_store_file not provided)
            play_store_pattern: Pattern for Play Store files (used if play_store_file not provided)
        """
        
        # Determine App Store file to use
        if app_store_file:
            if not os.path.exists(app_store_file):
                raise FileNotFoundError(f"App Store file not found: {app_store_file}")
            final_app_store_file = app_store_file
        else:
            # Use pattern-based selection (existing logic)
            app_store_files = glob.glob(app_store_pattern)
            if not app_store_files:
                raise FileNotFoundError(f"No App Store files found matching pattern: {app_store_pattern}")
            final_app_store_file = max(app_store_files, key=os.path.getctime)
        
        # Determine Play Store file to use
        if play_store_file:
            if not os.path.exists(play_store_file):
                raise FileNotFoundError(f"Play Store file not found: {play_store_file}")
            final_play_store_file = play_store_file
        else:
            # Use pattern-based selection (existing logic)
            play_store_files = glob.glob(play_store_pattern)
            if not play_store_files:
                raise FileNotFoundError(f"No Play Store files found matching pattern: {play_store_pattern}")
            final_play_store_file = max(play_store_files, key=os.path.getctime)
        
        print(f"Loading App Store data from: {final_app_store_file}")
        print(f"Loading Play Store data from: {final_play_store_file}")

        def _read_any(path: str) -> pd.DataFrame:
            lower = path.lower()
            if lower.endswith('.xlsx') or lower.endswith('.xls'):
                # First sheet by default
                try:
                    return pd.read_excel(path, engine='openpyxl')
                except Exception as ex:
                    print(f"Error reading Excel file {path}: {ex}")
                    raise
            # Default to CSV
            try:
                return pd.read_csv(path, on_bad_lines='skip', encoding='utf-8', low_memory=False)
            except Exception as e:
                print(f"Error reading CSV {path}: {e}")
                # Try alternative quoting if needed
                return pd.read_csv(path, on_bad_lines='skip', encoding='utf-8', quoting=1, low_memory=False)

        # Load the data
        app_store_df = _read_any(final_app_store_file)
        play_store_df = _read_any(final_play_store_file)
        
        print(f"App Store data: {len(app_store_df)} rows")
        print(f"Play Store data: {len(play_store_df)} rows")
        
        return app_store_df, play_store_df

    def map_app_store_data(self, df):
        """Map App Store data to target schema"""
        # Filter out corrupted rows (missing essential fields)
        df = df[df['title'].notna() & df['developer'].notna() & df['appId'].notna()]
        print(f"App Store data after filtering: {len(df)} rows")
        
        mapped_df = pd.DataFrame()
        
        # Initialize all target columns with NaN
        for col in self.target_columns:
            mapped_df[col] = np.nan
        
        # Map existing columns
        for source_col, target_col in self.app_store_mapping.items():
            if source_col in df.columns and target_col in self.target_columns:
                mapped_df[target_col] = df[source_col]
        
        # Set platform-specific fields
        mapped_df['store'] = 'Apple App Store'
        mapped_df['Platform_Technology'] = 'iOS'
        
        # Handle reviews mapping to reviews_appStore
        if 'reviews' in df.columns:
            mapped_df['reviews_appStore'] = df['reviews']
        
        return mapped_df

    def map_play_store_data(self, df):
        """Map Play Store data to target schema"""
        # Filter out corrupted rows (missing essential fields)
        df = df[df['title'].notna() & df['developer'].notna() & df['appId'].notna()]
        print(f"Play Store data after filtering: {len(df)} rows")
        
        mapped_df = pd.DataFrame()
        
        # Initialize all target columns with NaN
        for col in self.target_columns:
            mapped_df[col] = np.nan
        
        # Map existing columns
        for source_col, target_col in self.play_store_mapping.items():
            if source_col in df.columns and target_col in self.target_columns:
                mapped_df[target_col] = df[source_col]
        
        # Set platform-specific fields
        mapped_df['store'] = 'Google Play Store'
        mapped_df['Platform_Technology'] = 'Android'
        
        # Handle reviews mapping to reviews_playStore
        if 'reviews' in df.columns:
            mapped_df['reviews_playStore'] = df['reviews']
        
        return mapped_df

    def normalize_string_for_comparison(self, text):
        """Normalize strings for duplicate detection"""
        if pd.isna(text):
            return ""
        
        # Convert to lowercase, remove special characters, extra spaces
        normalized = str(text).lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized



    def find_duplicates(self, df):
        """Find duplicates based on matching appId values OR title + developer"""
        
        # Create normalized columns for comparison
        df['normalized_title'] = df['App_Name'].apply(self.normalize_string_for_comparison)
        df['normalized_developer'] = df['developer'].apply(self.normalize_string_for_comparison)
        
        # Create comparison keys
        df['title_dev_key'] = df['normalized_title'] + '_' + df['normalized_developer']
        
        duplicates = []
        
        # Group by matching appId values between platforms
        # Apps with same appId_appStore and appId_playStore are cross-platform
        for _, row in df.iterrows():
            if pd.notna(row.get('appId_appStore')) and pd.notna(row.get('appId_playStore')):
                if row['appId_appStore'] == row['appId_playStore']:
                    # Find all rows with this appId in either platform
                    matching_rows = df[
                        (df['appId_appStore'] == row['appId_appStore']) |
                        (df['appId_playStore'] == row['appId_playStore'])
                    ]
                    if len(matching_rows) > 1:
                        indices = matching_rows.index.tolist()
                        if not any(idx in [item for sublist in duplicates for item in sublist] 
                                  for idx in indices):
                            duplicates.append(indices)
        
        # Group by appId_appStore (same app on App Store)
        if 'appId_appStore' in df.columns:
            for appId, group in df.groupby('appId_appStore'):
                if pd.notna(appId) and str(appId).strip() != '' and len(group) > 1:
                    indices = group.index.tolist()
                    if not any(idx in [item for sublist in duplicates for item in sublist] 
                              for idx in indices):
                        duplicates.append(indices)
        
        # Group by appId_playStore (same app on Play Store)
        if 'appId_playStore' in df.columns:
            for appId, group in df.groupby('appId_playStore'):
                if pd.notna(appId) and str(appId).strip() != '' and len(group) > 1:
                    indices = group.index.tolist()
                    if not any(idx in [item for sublist in duplicates for item in sublist] 
                              for idx in indices):
                        duplicates.append(indices)
        
        # Group by id field if it exists (Apple Store numeric ID)
        if 'id' in df.columns:
            for app_id, group in df.groupby('id'):
                if pd.notna(app_id) and str(app_id).strip() != '' and len(group) > 1:
                    indices = group.index.tolist()
                    if not any(idx in [item for sublist in duplicates for item in sublist] 
                              for idx in indices):
                        duplicates.append(indices)
        
        # Group by title + developer as fallback
        for key, group in df.groupby('title_dev_key'):
            if len(group) > 1 and key.strip() != '_':
                indices = group.index.tolist()
                if not any(idx in [item for sublist in duplicates for item in sublist] 
                          for idx in indices):
                    duplicates.append(indices)
        
        return duplicates

    def merge_duplicate_rows(self, rows):
        """Merge duplicate rows, combining information from both platforms"""
        if len(rows) == 1:
            return rows.iloc[0]
        
        merged = rows.iloc[0].copy()
        
        # Define fields that should be kept separate for each platform
        platform_specific_fields = [
            'score_appStore', 'score_playStore', 
            'reviews_appStore', 'reviews_playStore',
            'price_appStore', 'price_playStore',
            'appId_appStore', 'appId_playStore',
            'genres_appStore', 'genreIds_appStore', 'primaryGenre_appStore', 'primaryGenreId',
            'genre_playStore', 'genreId_playStore', 'categories_playStore'
        ]
        
        # Define fields that should use first non-null (IDs, timestamps, etc.)
        first_non_null_fields = [
            'id', 'released', 'updated', 'version', 
            'contentRating', 'currency', 'free', 'developerId', 'developerInternalID',
            'sourceMethod', 'sourceCollection', 'sourceCountry', 'searchQuery', 'targetCategory'
        ]
        
        # Define fields that should be combined with separator (descriptive text)
        combinable_fields = [
            'description', 'descriptionHTML', 'summary', 'developer', 'developerUrl', 
            'developerWebsite', 'developerLegalName', 'privacyPolicy', 'url'
        ]
        
        for col in rows.columns:
            # Platform-specific fields: keep separate values from appropriate platform
            if col in platform_specific_fields:
                for _, row in rows.iterrows():
                    if pd.notna(row[col]):
                        merged[col] = row[col]
            
            # First non-null fields: use the first available value
            elif col in first_non_null_fields:
                non_null_values = rows[col].dropna()
                if len(non_null_values) > 0:
                    merged[col] = non_null_values.iloc[0]
            
            # Combinable fields: append values with separator
            elif col in combinable_fields:
                non_null_values = rows[col].dropna()
                if len(non_null_values) > 0:
                    # Remove duplicates while preserving order
                    unique_values = []
                    seen = set()
                    for val in non_null_values:
                        val_str = str(val).strip()
                        if val_str and val_str not in seen:
                            unique_values.append(val_str)
                            seen.add(val_str)
                    
                    if unique_values:
                        if len(unique_values) == 1:
                            merged[col] = unique_values[0]
                        else:
                            merged[col] = ' | '.join(unique_values)
            
            # Default: use first non-null value for any other fields
            else:
                non_null_values = rows[col].dropna()
                if len(non_null_values) > 0:
                    merged[col] = non_null_values.iloc[0]
        
        # Calculate average score if both platforms have scores
        if pd.notna(merged.get('score_appStore')) and pd.notna(merged.get('score_playStore')):
            merged['score_average'] = (float(merged['score_appStore']) + float(merged['score_playStore'])) / 2
            merged['availableOnBothPlatforms'] = True
        elif pd.notna(merged.get('score_appStore')) or pd.notna(merged.get('score_playStore')):
            merged['score_average'] = merged.get('score_appStore') or merged.get('score_playStore')
        
        # Calculate total reviews
        app_reviews = pd.to_numeric(merged.get('reviews_appStore'), errors='coerce') or 0
        play_reviews = pd.to_numeric(merged.get('reviews_playStore'), errors='coerce') or 0
        if app_reviews > 0 or play_reviews > 0:
            merged['reviews_total'] = app_reviews + play_reviews
        
        # Set platform field and store information
        platforms = []
        stores = []
        if pd.notna(merged.get('score_appStore')):
            platforms.append('iOS')
            stores.append('Apple App Store')
        if pd.notna(merged.get('score_playStore')):
            platforms.append('Android')
            stores.append('Google Play Store')
        
        if platforms:
            merged['platforms'] = ' | '.join(platforms)
            merged['store'] = ' | '.join(stores)
            merged['Platform_Technology'] = ' | '.join(platforms)
        else:
            # Keep existing values if no platform-specific scores found
            pass
        
        return merged

    def remove_duplicates(self, df):
        """Remove duplicates and merge information"""
        
        print("Finding duplicates...")
        duplicate_groups = self.find_duplicates(df)
        
        if not duplicate_groups:
            print("No duplicates found.")
            return df
        
        print(f"Found {len(duplicate_groups)} duplicate groups")
        
        # Create a set of indices to remove
        indices_to_remove = set()
        merged_rows = []
        
        for group_indices in duplicate_groups:
            # Get the rows for this duplicate group
            duplicate_rows = df.loc[group_indices]
            
            # Merge the duplicate rows
            merged_row = self.merge_duplicate_rows(duplicate_rows)
            merged_rows.append(merged_row)
            
            # Mark original indices for removal
            indices_to_remove.update(group_indices)
            
            print(f"Merged {len(group_indices)} duplicates for: {merged_row.get('App_Name', 'Unknown')}")
        
        # Remove original duplicate rows
        df_cleaned = df.drop(index=indices_to_remove)
        
        # Add merged rows
        if merged_rows:
            merged_df = pd.DataFrame(merged_rows)
            df_cleaned = pd.concat([df_cleaned, merged_df], ignore_index=True)
        
        print(f"After deduplication: {len(df_cleaned)} rows (removed {len(indices_to_remove) - len(merged_rows)} duplicates)")
        
        return df_cleaned

    def combine_data(self, app_store_df, play_store_df):
        """Combine App Store and Play Store data"""
        
        print("Mapping App Store data...")
        mapped_app_store = self.map_app_store_data(app_store_df)
        
        print("Mapping Play Store data...")
        mapped_play_store = self.map_play_store_data(play_store_df)
        
        print("Combining datasets...")
        combined_df = pd.concat([mapped_app_store, mapped_play_store], ignore_index=True)
        
        print("Removing duplicates...")
        final_df = self.remove_duplicates(combined_df)
        
        # Ensure all schema columns are present
        for col in self.target_columns:
            if col not in final_df.columns:
                final_df[col] = np.nan
        
        # Reorder columns to match schema
        final_df = final_df[self.target_columns]
        
        return final_df

    def export_data(self, df, output_prefix="COMBINED_apps"):
        """Export combined data to CSV and JSON"""
        
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%fZ")[:-3] + 'Z'
        
        csv_filename = f"{output_prefix}_{timestamp}.csv"
        json_filename = f"{output_prefix}_{timestamp}.json"
        
        print(f"Exporting to CSV: {csv_filename}")
        df.to_csv(csv_filename, index=False, sep=';')  # Use semicolon to match schema
        
        print(f"Exporting to JSON: {json_filename}")
        df.to_json(json_filename, orient='records', indent=2)
        
        # Also create a simple CSV without semicolons for easier viewing
        simple_csv = f"{output_prefix}_{timestamp}_simple.csv"
        print(f"Exporting simple CSV: {simple_csv}")
        df.to_csv(simple_csv, index=False)
        
        return csv_filename, json_filename, simple_csv

    def run_combination(self, app_store_file=None, play_store_file=None, 
                       app_store_pattern=None, play_store_pattern=None, output_prefix="COMBINED_apps"):
        """Run the complete combination process
        
        Args:
            app_store_file: Specific App Store file path
            play_store_file: Specific Play Store file path  
            app_store_pattern: Pattern for App Store files (fallback)
            play_store_pattern: Pattern for Play Store files (fallback)
            output_prefix: Prefix for output files
        """
        
        print("=== App Store and Play Store Data Combiner ===")
        print()
        
        # Use default patterns if not provided
        if app_store_pattern is None:
            app_store_pattern = "COMPLETE_appstore_*.csv"
        if play_store_pattern is None:
            play_store_pattern = "COMPLETE_playstore_*.csv"
        
        try:
            # Load data
            app_store_df, play_store_df = self.load_data_files(
                app_store_file=app_store_file,
                play_store_file=play_store_file,
                app_store_pattern=app_store_pattern, 
                play_store_pattern=play_store_pattern
            )
            
            # Combine data
            combined_df = self.combine_data(app_store_df, play_store_df)
            
            # Export results
            csv_file, json_file, simple_csv = self.export_data(combined_df, output_prefix)
            
            print()
            print("=== Summary ===")
            print(f"Total apps after combination: {len(combined_df)}")
            print(f"Apps available on both platforms: {len(combined_df[combined_df['availableOnBothPlatforms'] == True])}")
            print(f"iOS-only apps: {len(combined_df[combined_df['Platform_Technology'] == 'iOS'])}")
            print(f"Android-only apps: {len(combined_df[combined_df['Platform_Technology'] == 'Android'])}")
            print()
            print("Output files:")
            print(f"  - Schema CSV: {csv_file}")
            print(f"  - JSON: {json_file}")
            print(f"  - Simple CSV: {simple_csv}")
            
            return combined_df
            
        except Exception as e:
            print(f"Error during combination: {str(e)}")
            raise


def main():
    parser = argparse.ArgumentParser(description='Combine App Store and Play Store data')
    parser.add_argument('--app-store-file', 
                       help='Specific App Store CSV file path')
    parser.add_argument('--play-store-file', 
                       help='Specific Play Store CSV file path')
    parser.add_argument('--app-store-pattern', default="COMPLETE_appstore_*.csv",
                       help='Pattern for App Store CSV files (used if --app-store-file not provided)')
    parser.add_argument('--play-store-pattern', default="COMPLETE_playstore_*.csv",
                       help='Pattern for Play Store CSV files (used if --play-store-file not provided)')
    parser.add_argument('--output-prefix', default="COMBINED_apps",
                       help='Prefix for output files')
    
    args = parser.parse_args()
    
    combiner = AppStoreCombiner()
    combined_data = combiner.run_combination(
        app_store_file=args.app_store_file,
        play_store_file=args.play_store_file,
        app_store_pattern=args.app_store_pattern,
        play_store_pattern=args.play_store_pattern,
        output_prefix=args.output_prefix
    )


if __name__ == "__main__":
    main()
