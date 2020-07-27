import sys
sys.path.insert(0, "../")
import tldextract
import json

url_references = None
with open("../resources/url_references.json", "r") as fp:
    url_references = json.load(fp)

traversal_rules = dict()


