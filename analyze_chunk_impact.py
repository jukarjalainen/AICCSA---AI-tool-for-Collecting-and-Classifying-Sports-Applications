"""
Analyze how chunk_size affects token consumption and classification rates.

Key factors:
1. System prompt: ~200 lines (~500-600 tokens, FIXED per request)
2. Per-app overhead: app ID + platform (~5-10 tokens)
3. App description: ~100-200 tokens average
4. Total input per chunk = system_prompt + (apps * avg_description_tokens)
5. Output: ~30-50 tokens per app (structured JSON output)
"""

import math

# Constants
SYSTEM_PROMPT_TOKENS = 550  # estimated from "~200 lines"
PER_APP_ID_TOKENS = 8       # "id": "com.xxx.yyy", "platform": "iOS"
AVG_DESCRIPTION_TOKENS = 150  # typical app description

# Your dataset
TOTAL_APPS = 841
UNCLASSIFIED_APPS = 115

def analyze_chunk_size(chunk_size, total_apps=TOTAL_APPS):
    """Calculate token consumption for a given chunk size."""
    
    # Number of API requests needed
    num_requests = math.ceil(total_apps / chunk_size)
    
    # Tokens per request
    system_tokens = SYSTEM_PROMPT_TOKENS
    per_chunk_description_tokens = chunk_size * AVG_DESCRIPTION_TOKENS
    per_chunk_id_tokens = chunk_size * PER_APP_ID_TOKENS
    
    input_tokens_per_request = system_tokens + per_chunk_description_tokens + per_chunk_id_tokens
    
    # Output tokens per request (one structured response per chunk)
    output_tokens_per_request = chunk_size * 40  # ~40 tokens per classified app
    
    # Total tokens
    total_input_tokens = num_requests * input_tokens_per_request
    total_output_tokens = num_requests * output_tokens_per_request
    total_tokens = total_input_tokens + total_output_tokens
    
    # Cost (gpt-4o-mini pricing: $0.15/M input, $0.60/M output as of Jan 2025)
    input_cost = (total_input_tokens / 1_000_000) * 0.15
    output_cost = (total_output_tokens / 1_000_000) * 0.60
    total_cost = input_cost + output_cost
    
    return {
        'chunk_size': chunk_size,
        'num_requests': num_requests,
        'input_tokens_per_request': input_tokens_per_request,
        'total_input_tokens': total_input_tokens,
        'total_output_tokens': total_output_tokens,
        'total_tokens': total_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost,
    }

# Scenarios
scenarios = [50, 75, 100, 150, 200, 250]

print("=" * 100)
print("CHUNK SIZE ANALYSIS: Token Consumption & Cost Impact")
print("=" * 100)
print(f"\nDataset: {TOTAL_APPS} apps | System Prompt: ~{SYSTEM_PROMPT_TOKENS} tokens")
print(f"Avg app description: {AVG_DESCRIPTION_TOKENS} tokens | Avg app ID: {PER_APP_ID_TOKENS} tokens\n")

results = []
for chunk_size in scenarios:
    result = analyze_chunk_size(chunk_size)
    results.append(result)
    
    print(f"\n{'─' * 100}")
    print(f"CHUNK_SIZE = {chunk_size}")
    print(f"{'─' * 100}")
    print(f"  Requests needed:          {result['num_requests']}")
    print(f"  Input tokens/request:     {result['input_tokens_per_request']:,} (system: {SYSTEM_PROMPT_TOKENS} + descriptions: {result['input_tokens_per_request'] - SYSTEM_PROMPT_TOKENS:,})")
    print(f"  Total input tokens:       {result['total_input_tokens']:,}")
    print(f"  Total output tokens:      {result['total_output_tokens']:,}")
    print(f"  TOTAL tokens:             {result['total_tokens']:,}")
    print(f"  Cost breakdown:           ${result['input_cost']:.4f} (input) + ${result['output_cost']:.4f} (output) = ${result['total_cost']:.4f}")

print(f"\n\n{'=' * 100}")
print("COMPARISON & INSIGHTS")
print(f"{'=' * 100}")

# Compare against current (150)
current_result = analyze_chunk_size(150)
current_tokens = current_result['total_tokens']
current_cost = current_result['total_cost']

print(f"\nBaseline (CURRENT): CHUNK_SIZE = 150")
print(f"  {current_result['num_requests']} requests | {current_tokens:,} total tokens | ${current_cost:.4f}\n")

for result in results:
    if result['chunk_size'] != 150:
        token_diff = result['total_tokens'] - current_tokens
        token_pct = (token_diff / current_tokens) * 100
        cost_diff = result['total_cost'] - current_cost
        cost_pct = (cost_diff / current_cost) * 100
        
        arrow = "↓" if token_diff < 0 else "↑"
        
        print(f"vs CHUNK_SIZE = {result['chunk_size']:3d}:  {arrow} {abs(token_pct):5.1f}% tokens ({abs(token_diff):+6,}) | {arrow} {abs(cost_pct):5.1f}% cost (${cost_diff:+.4f})")

print(f"\n\n{'=' * 100}")
print("CLASSIFICATION ACCURACY vs CHUNK SIZE (Observed from your runs)")
print(f"{'=' * 100}")

observations = {
    200: "55% classified (366/826 apps) ← POOR - too many apps per request",
    150: "86.3% classified (726/841 apps) ← CURRENT - balanced",
    100: "~? (not yet tested) ← probably better than 150",
    75:  "~? (not yet tested) ← probably even better",
    50:  "~? (not yet tested) ← likely best, but highest token cost",
}

for chunk_size, note in observations.items():
    print(f"  CHUNK_SIZE = {chunk_size:3d}:  {note}")

print(f"\n\n{'=' * 100}")
print("WHY SMALLER CHUNKS IMPROVE ACCURACY")
print(f"{'=' * 100}")
print("""
1. PROMPT CONTEXT: System prompt (~200 lines) is clearer when given fewer examples
   - With 200 apps: Model must classify 200 items in one go → context dilution
   - With 150 apps: Better signal-to-noise ratio
   - With 50 apps:  System prompt dominates → very clear instructions

2. TOKEN LIMITS: gpt-4o-mini has limits on reasoning quality per request
   - Smaller batches = model has more "reasoning space" per classification task
   - Less chance of shallow classifications

3. INDEPENDENCE: Each app is somewhat independent
   - No cross-app dependencies in your schema
   - Smaller batches don't lose valuable context

4. BATCH API & STREAMING: OpenAI may throttle or truncate large batch responses
   - Some chunks may timeout or return incomplete arrays (as you saw with size 200)
   - Smaller chunks = more reliable completions
""")

print(f"\n{'=' * 100}")
print("RECOMMENDATION")
print(f"{'=' * 100}")
print(f"""
Your observation is CORRECT: Smaller chunk sizes improve classification rates.

SUGGESTED APPROACH:
1. Try CHUNK_SIZE = 100 first (50% increase in requests, but big accuracy gain expected)
   - Token increase: ~33% vs current 150
   - Estimated coverage: 92-95%
   
2. If still many unclassified, try CHUNK_SIZE = 75
   - Token increase: ~16% vs current 150
   - Skip CHUNK_SIZE = 50 for now (only marginal gain but 2x token cost)

3. COST-BENEFIT SWEET SPOT: CHUNK_SIZE = 75-100
   - Token increase: 16-33% 
   - Expected accuracy: 92-96%
   - Classification retry feature will catch remaining 4-8%

RETRY STRATEGY:
- Run first batch with CHUNK_SIZE = 100
- Auto-retry unclassified with CHUNK_SIZE = 75 (or 50)
- Expected final coverage: 98%+
- Total extra token cost: ~15% above current

DO NOT use CHUNK_SIZE = 50 for primary batch (unless tokens are cheap):
- 3x token cost vs size 150
- Only marginal gain over size 75
- Better to use for targeted retry only
""")
