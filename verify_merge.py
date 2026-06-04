import re

# Check merge_results.py
with open('backend/openAIBatchClassifier/src/merge_results.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
print("=== Checking merge_results.py ===")

# Check target_cols
if 'target_cols = [\n        "not_relevant",' in content:
    print("✅ target_cols uses 'not_relevant' as first item")
elif '"is_relevant"' in content and 'target_cols' in content:
    print("❌ Still has 'is_relevant' in target_cols")
else:
    print("⚠️  Could not verify target_cols")

# Check column resolution
if '"not_relevant": _resolve_column(df, ["not_relevant"' in content:
    print("✅ _resolve_classification_columns maps 'not_relevant'")
else:
    print("❌ 'not_relevant' not in column resolution")

# Check that it preserves not_relevant instead of negating
if 'preds["not_relevant"] = preds["not_relevant"].map(lambda v: "TRUE" if bool(v) else "FALSE")' in content:
    print("✅ Correctly preserves 'not_relevant' as TRUE/FALSE")
elif '(~preds["not_relevant"])' in content:
    print("❌ Still negating not_relevant")
else:
    print("⚠️  Could not verify not_relevant handling")
