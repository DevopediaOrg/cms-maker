import pickle
import json
from CMS import Format

with open("../resources/references.pkl", "rb") as dump_file:
    references = pickle.load(dump_file)

for article_title in references:
    print(article_title)
    print("Uncleaned", len(references[article_title]))
    references[article_title] = [x for x in references[article_title] if x]
    print("Cleaned", len(references[article_title]))
    print("\n")

with open("../resources/references.json", "w") as dump_file:
    json.dump(references, dump_file, cls=Format.MyEncoder)
