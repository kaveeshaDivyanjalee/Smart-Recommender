import gzip
import json
import pandas as pd

# Convert Electronics.jsonl.gz to Electronics.csv.gz
INPUT_PATH = "data/Electronics.jsonl.gz"
OUTPUT_PATH = "data/Electronics.csv.gz"

rows = []

with gzip.open(INPUT_PATH, 'rt', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        row = {
            'user_id': data.get('user_id'),
            'parent_asin': data.get('parent_asin'),
            'rating': data.get('rating'),
            'timestamp': data.get('timestamp')
        }
        rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(OUTPUT_PATH, index=False, compression='gzip')

print("Converted and saved:", df.shape)