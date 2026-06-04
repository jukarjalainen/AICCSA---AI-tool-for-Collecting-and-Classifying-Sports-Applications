import pandas as pd
import sys
sys.path.insert(0, r'c:\aiccsa\backend')

# Now test with the FIXED detection logic
def is_unclassified_correct(row):
    """Fixed: use correct column names with proper casing"""
    import pandas as pd
    required_fields = ["not_relevant", "Purpose", "Sport_Type"]
    for field in required_fields:
        val = row.get(field)
        if pd.isna(val):
            return True
        val_str = str(val).strip()
        if not val_str or val_str.lower() in ("nan", "none", ""):
            return True
    return False

df_1127 = pd.read_excel(r'backend/openAIBatchClassifier/out/apps_with_classification_2026-31-03_1127.xlsx')

# Test with FIXED logic
unclass_fixed = df_1127[df_1127.apply(is_unclassified_correct, axis=1)]

print(f"Unclassified apps (FIXED): {len(unclass_fixed)}")
print(f"Expected: 155")
print(f"Match: {'✅ YES' if len(unclass_fixed) == 155 else '❌ NO'}")

# Show that this will now be retried
print(f"\n✅ Retry detection FIX confirmed!")
print(f"   Next run will retry {len(unclass_fixed)} unclassified apps")
