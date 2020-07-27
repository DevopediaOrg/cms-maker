import sys

sys.path.insert(0, "../")
import json
from CMS import Format

with open("../resources/url_references.json", "r") as url_references:
    url_references = json.load(url_references)

stats_keys = ['ALL_VALUES_PRESENT', 'PRESENT_VALUES']
stats = dict()
stats["pdf"] = 0
for i in Format.AuthorDateFormat.KEYS:
    stats[i] = 0


for url in url_references:
    result = url_references[url]
    if ".pdf" in url:
        stats["pdf"] += 1
    all_values_present = True
    if result:
        for key in Format.AuthorDateFormat.KEYS:
            if key in result and result[key]:
                stats[key] += 1
            else:
                all_values_present = False
print(stats)



