import pandas as pd

# Read both files
df_old = pd.read_excel(r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_0917.xlsx')
df_new = pd.read_excel(r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_1048.xlsx')

# Check for unclassified
def is_unclassified(row):
    required_fields = ["not_relevant", "Purpose", "Sport_Type"]
    for field in required_fields:
        if pd.isna(row[field]):
            return True
    return False

unclass_old = set(df_old[df_old.apply(is_unclassified, axis=1)]["App_ID"].values)
unclass_new = set(df_new[df_new.apply(is_unclassified, axis=1)]["App_ID"].values)

# Find the 10 apps that became unclassified (regressed)
newly_unclassified = unclass_new - unclass_old

print(f"Apps that were CLASSIFIED in 0917 but became UNCLASSIFIED in 1048:")
print(f"Count: {len(newly_unclassified)}\n")

if len(newly_unclassified) > 0:
    # Get details about these apps from the new file
    mask = df_new["App_ID"].isin(newly_unclassified)
    regression_apps = df_new[mask][["App_ID", "App_Name", "Is_relevant", "Purpose", "Sport_Type"]].copy()
    print(regression_apps.to_string())
else:
    print("None found")

# Also check if any previously unclassified became classified (improvement)
newly_classified = unclass_old - unclass_new
print(f"\n\nApps that were UNCLASSIFIED in 0917 but became CLASSIFIED in 1048:")
print(f"Count: {len(newly_classified)}")
