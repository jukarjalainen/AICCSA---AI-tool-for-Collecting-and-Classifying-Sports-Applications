import json

# Check the first retry descriptions to see which apps were supposed to be retried
with open(r'backend/openAIBatchClassifier/out/descriptions_retry.jsonl', 'r') as f:
    retry_desc_ids = []
    for line in f:
        if line.strip():
            obj = json.loads(line)
            retry_desc_ids.append(obj['id'])

print(f"Apps sent for retry: {len(retry_desc_ids)}")
print(f"Sample retry IDs: {retry_desc_ids[:5]}")

# Now check the batch output
with open(r'backend/openAIBatchClassifier/out/batch_output.jsonl1', 'r') as f:
    batch_ids = []
    for line in f:
        if line.strip():
            try:
                obj = json.loads(line)
                content = obj["response"]["body"]["choices"][0]["message"]["content"]
                content_str = content.strip()
                start = content_str.find('[')
                end = content_str.rfind(']')
                if start != -1 and end != -1:
                    parsed = json.loads(content_str[start:end+1])
                    if isinstance(parsed, list):
                        for item in parsed:
                            batch_ids.append(item.get('id'))
            except:
                pass

print(f"\nApps in batch output: {len(batch_ids)}")
print(f"Sample output IDs: {batch_ids[:5]}")

# Check overlap
retry_set = set(retry_desc_ids)
batch_set = set(batch_ids)
overlap = retry_set & batch_set

print(f"\nOverlap between retry descriptions and batch output: {len(overlap)}")
print(f"In retry but not in batch: {len(retry_set - batch_set)}")
print(f"In batch but not in retry: {len(batch_set - retry_set)}")
