import json
import re

with open("C:/niji-uta/scratch/kaida_comment_raw.json", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'(\d{1,2}:\d{2}\s*[^\n\r\\"]*シャルル[^\n\r\\"]*)', text)
print("Regex matches for シャルル in raw json:", matches)

# 24:26 の前後50文字
pos = text.find("24:26")
if pos != -1:
    print("Surrounding 24:26:\n", text[pos-30:pos+80])
