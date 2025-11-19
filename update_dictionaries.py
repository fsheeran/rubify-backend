#!/usr/bin/env python3
import os
import requests
import tarfile
import json
from collections import defaultdict

# URL of the tar.gz file to download
url = "https://github.com/Doublevil/JmdictFurigana/releases/latest/download/JmdictFurigana.json.tar.gz"

filepath = "jmdictfurigana.tar.gz"

response = requests.get(url)

with open(filepath, "wb") as file:
    file.write(response.content)

with tarfile.open(filepath, "r:gz") as tar:
    tar.extractall(filter="data")

os.remove(filepath)

with open("JmdictFurigana.json", "r", encoding="utf-8-sig") as f:
    raw_furigana_data = json.load(f)

transformed_furigana_data = defaultdict(list)
for entry in raw_furigana_data:
    text = entry.pop("text")
    per_char = []
    ruby_start = 0
    ruby_end = 0
    for fg in entry["furigana"]:
        if not fg.get("rt"):
            continue

        ruby_start = text.find(fg["ruby"], ruby_end)
        ruby_end = ruby_start + len(fg["ruby"])
        per_char.append(
            {"indices": (ruby_start, ruby_end), "pronunciation": fg["rt"]}
        )

    if not per_char:
        continue

    transformed_furigana_data[text].append(
        {
            "pronunciation": entry["reading"],
            "per_char": per_char,
        }
    )

with open("JmdictFurigana.json", "w", encoding="utf-8") as f:
    json.dump(transformed_furigana_data, f, ensure_ascii=False)
