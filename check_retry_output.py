import json
import pandas as pd

# Read the retry batch output
output_file = r'backend/openAIBatchClassifier/out/batch_output.jsonl1'
classifications = []

with open(output_file, 'r') as f:
    for line in f:
        if line.strip():
            try:
                obj = json.loads(line)
                content = obj["response"]["body"]["choices"][0]["message"]["content"]
                # Extract JSON array
                content_str = content.strip()
                start = content_str.find('[')
                end = content_str.rfind(']')
                if start != -1 and end != -1:
                    try:
                        parsed = json.loads(content_str[start:end+1])
                        if isinstance(parsed, list):
                            classifications.extend(parsed)
                    except:
                        pass
            except:
                pass

print(f"Total classifications in retry batch output: {len(classifications)}")
if classifications:
    print(f"\nSample classification:")
    print(json.dumps(classifications[0], indent=2))
    
    # Check how many have non-empty is_relevant
    with_relevant = sum(1 for c in classifications if pd.notna(c.get('is_relevant')) and c.get('is_relevant') not in ('', 'NaN', 'nan'))
    print(f"\n\nWith is_relevant (non-empty): {with_relevant}/{len(classifications)}")
    
    # Check purpose and sport_type too
    with_purpose = sum(1 for c in classifications if pd.notna(c.get('purpose')) and c.get('purpose') not in ('', 'NaN', 'nan'))
    with_sport = sum(1 for c in classifications if pd.notna(c.get('sport_type')) and c.get('sport_type') not in ('', 'NaN', 'nan'))
    
    print(f"With purpose (non-empty): {with_purpose}/{len(classifications)}")
    print(f"With sport_type (non-empty): {with_sport}/{len(classifications)}")
    
    # Count fully complete classifications
    fully_complete = sum(1 for c in classifications if 
        pd.notna(c.get('is_relevant')) and c.get('is_relevant') not in ('', 'NaN', 'nan') and
        pd.notna(c.get('purpose')) and c.get('purpose') not in ('', 'NaN', 'nan') and
        pd.notna(c.get('sport_type')) and c.get('sport_type') not in ('', 'NaN', 'nan')
    )
    print(f"Fully complete: {fully_complete}/{len(classifications)}")
