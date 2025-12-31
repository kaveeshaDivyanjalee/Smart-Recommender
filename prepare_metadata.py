import gzip
import json
import pandas as pd

INPUT_PATH = "data/meta_Electronics.jsonl.gz"
OUTPUT_PATH = "data/asin_title_map.csv"

rows = []

with gzip.open(INPUT_PATH, 'rt', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        asin = data.get("parent_asin") or data.get("asin")
        title = data.get("title")
        if asin and title:
            rows.append((asin, title))

df = pd.DataFrame(rows, columns=["asin", "title"])
df.to_csv(OUTPUT_PATH, index=False)

print("Saved:", df.shape)