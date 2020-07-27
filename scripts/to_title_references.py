import json
import sys
sys.path.insert(0, '../')
from CMS import Format
with open("../resources/references.json", "r") as references_file:
    title_cms_references = json.load(references_file)

title_references = dict()
for key in title_cms_references:
    title_references[key] = [cms["url"] for cms in title_cms_references[key]]

with open("../resources/title_references.json", "w") as title_references_file:
    json.dump(title_references, title_references_file)