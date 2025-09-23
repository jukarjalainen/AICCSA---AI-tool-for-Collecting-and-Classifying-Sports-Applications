#!/usr/bin/env python3
"""
Check if datasets have missing appId fields
"""

import pandas as pd
import glob
import os

def check_app_ids():
    # Find the most recent files
    app_files = glob.glob('COMPLETE_appstore_*.csv')
    play_files = glob.glob('COMPLETE_playstore_*.csv')
    
    if app_files:
        app_file = max(app_files, key=os.path.getctime)
        print(f"Checking App Store file: {app_file}")
        app_df = pd.read_csv(app_file, on_bad_lines='skip', encoding='utf-8')
        
        print(f"App Store - Total rows: {len(app_df)}")
        print(f"App Store columns: {list(app_df.columns)}")
        
        if 'appId' in app_df.columns:
            missing_appid = app_df['appId'].isna().sum()
            print(f"App Store - Missing appId: {missing_appid}")
            if missing_appid > 0:
                print("Sample rows with missing appId:")
                print(app_df[app_df['appId'].isna()][['title', 'developer']].head())
        
        if 'id' in app_df.columns:
            missing_id = app_df['id'].isna().sum()
            print(f"App Store - Missing id: {missing_id}")
            if missing_id > 0:
                print("Sample rows with missing id:")
                print(app_df[app_df['id'].isna()][['title', 'developer']].head())
    
    print("\n" + "="*50 + "\n")
    
    if play_files:
        play_file = max(play_files, key=os.path.getctime)
        print(f"Checking Play Store file: {play_file}")
        play_df = pd.read_csv(play_file, on_bad_lines='skip', encoding='utf-8')
        
        print(f"Play Store - Total rows: {len(play_df)}")
        print(f"Play Store columns: {list(play_df.columns)}")
        
        if 'appId' in play_df.columns:
            missing_appid = play_df['appId'].isna().sum()
            print(f"Play Store - Missing appId: {missing_appid}")
            if missing_appid > 0:
                print("Sample rows with missing appId:")
                print(play_df[play_df['appId'].isna()][['title', 'developer']].head())
        
        if 'id' in play_df.columns:
            missing_id = play_df['id'].isna().sum()
            print(f"Play Store - Missing id: {missing_id}")
            if missing_id > 0:
                print("Sample rows with missing id:")
                print(play_df[play_df['id'].isna()][['title', 'developer']].head())

if __name__ == "__main__":
    check_app_ids()
