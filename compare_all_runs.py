import pandas as pd

# Read all three files
files = {
    '0917': r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_0917.xlsx',
    '1048': r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_1048.xlsx',
    '1127': r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_1127.xlsx',
}

results = {}

# Check for unclassified - support both column name variations
def is_unclassified(row):
    # Try both possible column names for not_relevant/is_relevant
    relevant_cols = ["not_relevant", "Not_relevant", "Is_relevant", "is_relevant"]
    purpose_cols = ["Purpose", "purpose"]
    sport_cols = ["Sport_Type", "sport_type"]
    
    # Find which column exists
    relevant_col = None
    for col in relevant_cols:
        if col in row.index:
            relevant_col = col
            break
    
    purpose_col = None
    for col in purpose_cols:
        if col in row.index:
            purpose_col = col
            break
    
    sport_col = None
    for col in sport_cols:
        if col in row.index:
            sport_col = col
            break
    
    # Check for NaN in any required field
    if relevant_col and pd.isna(row[relevant_col]):
        return True
    if purpose_col and pd.isna(row[purpose_col]):
        return True
    if sport_col and pd.isna(row[sport_col]):
        return True
    
    return False

for label, filepath in files.items():
    try:
        df = pd.read_excel(filepath)
        unclass = df[df.apply(is_unclassified, axis=1)]
        classified = len(df) - len(unclass)
        coverage = (100 * classified / len(df))
        
        results[label] = {
            'total': len(df),
            'classified': classified,
            'unclassified': len(unclass),
            'coverage': coverage,
            'df': df,
            'unclass_df': unclass,
        }
        print(f"✓ Loaded {label}")
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")

print("\n" + "="*90)
print("CLASSIFICATION COVERAGE COMPARISON")
print("="*90)

if len(results) >= 2:
    for label in ['0917', '1048', '1127']:
        if label not in results:
            continue
        r = results[label]
        print(f"\n{label} ({r['total']} apps):")
        print(f"  Classified:   {r['classified']:3d} ({r['coverage']:5.1f}%)")
        print(f"  Unclassified: {r['unclassified']:3d} ({100-r['coverage']:5.1f}%)")

    # Comparisons
    print("\n" + "-"*90)
    print("PROGRESSION")
    print("-"*90)
    
    if '0917' in results and '1048' in results:
        diff_0917_to_1048 = results['1048']['classified'] - results['0917']['classified']
        print(f"\n0917 → 1048: {diff_0917_to_1048:+d} classified ({diff_0917_to_1048/results['0917']['classified']*100:+.1f}%)")
        print(f"  Coverage: 86.3% → 85.1%")
    
    if '1048' in results and '1127' in results:
        diff_1048_to_1127 = results['1127']['classified'] - results['1048']['classified']
        pct_change = (diff_1048_to_1127 / results['1048']['classified']) * 100
        print(f"\n1048 → 1127: {diff_1048_to_1127:+d} classified ({pct_change:+.1f}%)")
        print(f"  Coverage: 85.1% → {results['1127']['coverage']:.1f}%")
        
        if diff_1048_to_1127 > 0:
            print(f"  ✅ IMPROVEMENT: {diff_1048_to_1127} more apps classified!")
        elif diff_1048_to_1127 < 0:
            print(f"  ⚠️  REGRESSION: {abs(diff_1048_to_1127)} fewer apps classified")
        else:
            print(f"  ➡️  Same coverage")

    # Details about newly classified/unclassified
    if '1048' in results and '1127' in results:
        app_id_col_1048 = "App_ID" if "App_ID" in results['1048']['unclass_df'].columns else "app_id"
        app_id_col_1127 = "App_ID" if "App_ID" in results['1127']['unclass_df'].columns else "app_id"
        
        unclass_1048 = set(results['1048']['unclass_df'][app_id_col_1048].values)
        unclass_1127 = set(results['1127']['unclass_df'][app_id_col_1127].values)
        
        newly_classified = unclass_1048 - unclass_1127
        newly_unclassified = unclass_1127 - unclass_1048
        
        print(f"\nDETAILS (1048 → 1127):")
        print(f"  Apps that became CLASSIFIED:   {len(newly_classified)}")
        print(f"  Apps that became UNCLASSIFIED: {len(newly_unclassified)}")
        
        if len(newly_classified) > 0:
            print(f"\n  Sample newly classified (first 5):")
            app_id_col = "App_ID" if "App_ID" in results['1127']['df'].columns else "app_id"
            mask = results['1127']['df'][app_id_col].isin(list(newly_classified)[:5])
            display_cols = [app_id_col, "App_Name" if "App_Name" in results['1127']['df'].columns else "title", 
                           "not_relevant" if "not_relevant" in results['1127']['df'].columns else "Is_relevant", 
                           "Purpose", "Sport_Type"]
            cols_exist = [c for c in display_cols if c in results['1127']['df'].columns]
            print(results['1127']['df'][mask][cols_exist].to_string())

print("\n" + "="*90)
