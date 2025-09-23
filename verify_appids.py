#!/usr/bin/env python3
"""
Verify platform-specific appId fields
"""

import pandas as pd

def verify_appid_fields():
    df = pd.read_csv('COMBINED_apps_2025-08-20T13-13-31-4599Z.csv', sep=';')
    
    print('Platform-specific appId verification:')
    print(f'Apps with appId_appStore: {df["appId_appStore"].notna().sum()}')
    print(f'Apps with appId_playStore: {df["appId_playStore"].notna().sum()}')
    
    cross_platform = df[df['availableOnBothPlatforms'] == True]
    sample = cross_platform[['App_Name', 'appId_appStore', 'appId_playStore']].dropna(subset=['appId_appStore', 'appId_playStore'])
    
    print(f'\nCross-platform apps with both appIds: {len(sample)}')
    if len(sample) > 0:
        print('\nSample cross-platform app:')
        print(sample.iloc[0].to_string())
        
        # Check if appIds match for cross-platform apps
        matching_appids = sample[sample['appId_appStore'] == sample['appId_playStore']]
        print(f'\nCross-platform apps with matching appIds: {len(matching_appids)}')
        if len(matching_appids) > 0:
            print('Example with matching appId:')
            print(matching_appids.iloc[0].to_string())

if __name__ == "__main__":
    verify_appid_fields()
