import json
from CMS import Format
import random

references = None
with open("../resources/references.json", "r") as dump_file:
    references = json.load(dump_file)

random_picks = list()
# random_picks.extend(random.choices(references, k = 3))
for i in range(3):
    random_picks.append(random.choice(list(references.keys())))

random_picks_references = list()
for k in random_picks:
    random_picks_references.extend(references[k])
random_ref_urls = []
for i in range(10):
    random_ref_urls.append(random.choice(random_picks_references)['url'])


with open("../urls.json", "w") as urls_json:
    json.dump(random_ref_urls, urls_json)