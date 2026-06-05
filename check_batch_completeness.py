import json
import pandas as pd

print("Analyzing batch_output.jsonl1 (9 lines)")
print("=" * 90)

classifications_total = 0
classifications_list = []
fields_present = {'not_relevant': 0, 'purpose': 0, 'sport_type': 0}
fields_missing = {'not_relevant': 0, 'purpose': 0, 'sport_type': 0}

with open(r'backend/openAIBatchClassifier/out/batch_output.jsonl1', 'r') as f:
    for line_num, line in enumerate(f, 1):
        try:
            obj = json.loads(line)
            content = obj["response"]["body"]["choices"][0]["message"]["content"]
            
            # Extract JSON array
            content_str = content.strip()
            start = content_str.find('[')
            end = content_str.rfind(']')
            
            if start != -1 and end != -1:
                parsed = json.loads(content_str[start:end+1])
                if isinstance(parsed, list):
                    batch_apps = len(parsed)
                    classifications_total += batch_apps
                    classifications_list.extend(parsed)
                    
                    # Count field presence
                    for item in parsed:
                        for field in ['not_relevant', 'purpose', 'sport_type']:
                            if pd.notna(item.get(field)):
                                fields_present[field] += 1
                            else:
                                fields_missing[field] += 1
                    
                    print(f"Line {line_num}: {batch_apps} classifications")
        except Exception as e:
            print(f"Line {line_num}: Error - {str(e)[:50]}")

print(f"\n{'─'*90}")
print(f"Total classifications: {classifications_total}")
print(f"Average per batch: {classifications_total // 9 if classifications_total > 0 else 0}")

print(f"\nField Completeness:")
total_items = classifications_total
if total_items > 0:
    for field in ['not_relevant', 'purpose', 'sport_type']:
        present = fields_present[field]
        missing = fields_missing[field]
        pct = (present / total_items) * 100 if total_items > 0 else 0
        print(f"  {field:15s}: {present:4d}/{total_items:4d} ({pct:5.1f}%) present")

print(f"\n{'─'*90}")
print(f"Expected apps in 1127 file: 832")
print(f"Actual classifications from batch: {classifications_total}")
print(f"Difference: {832 - classifications_total} apps missing from batch output")

if classifications_total < 832:
    print(f"\n⚠️  BATCH INCOMPLETE: Only {classifications_total}/{832} apps got classifications")
    print(f"    This explains the low 81.4% coverage!")
    print(f"\nSample classifications (first 3):")
    for i, item in enumerate(classifications_list[:3]):
        print(f"  {i+1}. ID: {item.get('id')}, not_relevant: {item.get('not_relevant')}, purpose: {item.get('purpose')}, sport: {item.get('sport_type')}")
