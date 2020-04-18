import json

with open("../resources/references.json", "r") as dump_file:
    references = json.load(dump_file)

url_ref_dict = dict()
for refs_key in references:
    refs = references[refs_key]
    for ref in refs:
        ref['article'] = refs_key
        url_ref_dict[ref['url']] = ref


with open("../resources/url_references.json", "w") as dump_file:
    json.dump(url_ref_dict, dump_file)
