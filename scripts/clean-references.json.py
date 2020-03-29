import pickle
import json
import CMS

with open("../resources/references.pkl", "rb") as dump_file:
    references = pickle.load(dump_file)

for article_title in references:
    print(len(references[article_title]))
    references[article_title] = [x for x in references[article_title] if x]

with open("../resources/references.json", "w") as dump_file:
    json.dump(references, dump_file, cls=CMS.MyEncoder)
