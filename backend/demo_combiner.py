#!/usr/bin/env python3
"""
Demonstration script for the App Store and Play Store Data Combiner

This script shows how to use the combiner and provides some basic analysis
of the combined data.
"""

import pandas as pd
from combiner.combine_app_stores_advanced import AppStoreCombiner

def analyze_combined_data(filename):
    """Analyze the combined data and provide insights"""
    
    print("=== Combined Data Analysis ===")
    print()
    
    # Load the combined data
    df = pd.read_csv(filename)
    
    print(f"Total apps in combined dataset: {len(df)}")
    print()
    
    # Platform distribution
    print("Platform Distribution:")
    platform_counts = df['Platform_Technology'].value_counts()
    for platform, count in platform_counts.items():
        print(f"  {platform}: {count} apps")
    print()
    
    # Apps available on both platforms
    both_platforms = df[df['availableOnBothPlatforms'] == True]
    print(f"Apps available on both platforms: {len(both_platforms)}")
    print()
    
    # Score analysis
    print("Score Analysis:")
    apple_scores = df[df['score_appStore'].notna()]['score_appStore']
    play_scores = df[df['score_playStore'].notna()]['score_playStore']
    
    if len(apple_scores) > 0:
        print(f"  Apple App Store average score: {apple_scores.mean():.2f}")
    if len(play_scores) > 0:
        print(f"  Google Play Store average score: {play_scores.mean():.2f}")
    print()
    
    # Developer analysis
    print("Top Developers (by number of apps):")
    top_developers = df['developer'].value_counts().head(10)
    for dev, count in top_developers.items():
        if pd.notna(dev):
            print(f"  {dev}: {count} apps")
    print()
    
    # Free vs Paid
    print("Free vs Paid Apps:")
    free_counts = df['free'].value_counts()
    for free_status, count in free_counts.items():
        status = "Free" if free_status == True else "Paid" if free_status == False else "Unknown"
        print(f"  {status}: {count} apps")
    print()

def main():
    """Main demonstration function"""
    
    print("=== App Store and Play Store Data Combiner Demo ===")
    print()
    
    # Initialize the combiner
    combiner = AppStoreCombiner()
    
    # Run the combination process
    try:
        combined_df = combiner.run_combination()
        
        print()
        print("=== Analysis of Combined Data ===")
        
        # Analyze the latest combined file
        import glob
        combined_files = glob.glob("COMBINED_apps_*_simple.csv")
        if combined_files:
            latest_file = max(combined_files, key=lambda x: x.split('_')[-2])
            analyze_combined_data(latest_file)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure you have COMPLETE_appstore_*.csv and COMPLETE_playstore_*.csv files in the directory")
    except Exception as e:
        print(f"Error during combination: {e}")

if __name__ == "__main__":
    main()
