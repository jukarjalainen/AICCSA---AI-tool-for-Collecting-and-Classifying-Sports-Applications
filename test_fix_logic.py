import pandas as pd
import sys
sys.path.insert(0, 'backend/openAIBatchClassifier')

# Load the file
df = pd.read_excel('backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_1158.xlsx')

# Apply the fix logic
not_relevant_col = 'not_relevant'
classification_cols = ['Purpose', 'Sport_Type', 'athlete', 'supporter', 'support_staff', 'governing_entity']

# If not_relevant = TRUE, set all classification fields to "UNKNOWN"
not_relevant_mask = (df[not_relevant_col].fillna("").astype(str).str.strip().str.upper() == "TRUE")
for col in classification_cols:
    df.loc[not_relevant_mask, col] = "UNKNOWN"
    # Also set empty/NaN values to "UNKNOWN" for relevant apps
    df.loc[~not_relevant_mask, col] = df.loc[~not_relevant_mask, col].fillna("UNKNOWN").astype(str).str.strip()
    df.loc[(~not_relevant_mask) & (df[col] == ""), col] = "UNKNOWN"

# Count results
print('=== AFTER FIX ===')
print(f'Total apps: {len(df)}')
print(f'\nClassification coverage:')

# Count fully classified apps (no UNKNOWN, no NaN)
fully_classified = 0
unknown_count = 0
nan_count = 0

for idx, row in df.iterrows():
    has_unknown = any(row[col] == 'UNKNOWN' for col in classification_cols)
    has_nan = any(pd.isna(row[col]) for col in classification_cols)
    
    if has_nan:
        nan_count += 1
    elif has_unknown:
        unknown_count += 1
    else:
        fully_classified += 1

print(f'Fully classified (no UNKNOWN, no NaN): {fully_classified}')
print(f'With UNKNOWN values: {unknown_count}')
print(f'With NaN values: {nan_count}')

# Verify the logic
nr_true_check = df[df['not_relevant'] == True]
all_unknown = nr_true_check[classification_cols].isin(['UNKNOWN']).all(axis=1).sum()
print(f'\nVerification:')
print(f'Apps with not_relevant=TRUE that have all UNKNOWN: {all_unknown} (should be {len(nr_true_check)})')

print(f'\nNow ready to re-run pipeline with fixed logic!')
