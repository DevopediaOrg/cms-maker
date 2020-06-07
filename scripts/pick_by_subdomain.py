import sys
sys.path.insert(0, '../')
import json
with open("../resources/url_references.json", "r") as url_references:
    url_references = json.load(url_references)

domains = ["medium.com", "linkedin.com", "analyticsvidhya.com"]
domain_url_references = dict()
for domain in domains:
    domain_url_references[domain] = list()
picked_references = list()
for reference in url_references:
    for domain in domains:
        if domain in reference:
            domain_url_references[domain].append(url_references[reference])
            picked_references.append(reference)
            break

with open("../resources/domain_url_references.json", "w") as domain_url_references_fp:
    json.dump(domain_url_references, domain_url_references_fp)

with open("../resources/picked_references.json", "w") as picked_references_fp:
    json.dump(picked_references, picked_references_fp)

