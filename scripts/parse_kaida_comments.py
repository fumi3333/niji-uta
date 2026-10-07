import json
import re

with open("C:/niji-uta/scratch/kaida_comment_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# レンダラーからコメントテキストを走査
data_str = json.dumps(data, ensure_ascii=False)
comments = re.findall(r'"contentText":\{"runs":\[(.*?)\]\}', data_str)

print(f"Total comments found: {len(comments)}")
setlist_lines = []
for c in comments:
    # runsからtextを結合
    texts = re.findall(r'"text":"([^"]+)"', c)
    full_text = "".join(texts)
    if "シャルル" in full_text or "24:26" in full_text:
        print("--- MATCHED COMMENT ---")
        for line in full_text.split("\n"):
            if any(char.isdigit() for char in line) and ":" in line:
                print(line)
