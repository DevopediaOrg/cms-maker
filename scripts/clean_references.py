import sys
sys.path.insert(0, '../')

import pickle
import json
from CMS import Format

with open("../resources/references.pkl", "rb") as dump_file:
    references = pickle.load(dump_file)
new_references = dict()
for article_title in references:
    print(article_title)
    new_references[article_title] = [x for x in references[article_title] if x]
    if len(references[article_title]) != len(new_references[article_title]):
        print("Mismatch:", len(references[article_title]), len(new_references[article_title]))
references = new_references
with open("../resources/references.pkl", "wb") as dump_file:
    pickle.dump(references, dump_file)

with open("../resources/references.json", "w") as dump_file:
    json.dump(references, dump_file, cls=Format.MyEncoder)
