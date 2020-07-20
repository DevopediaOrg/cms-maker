import json
with open("../resources/urls_by_domains.json", "r") as fp:
    urls_by_domain = json.load(fp)

urls = list()
for domain in urls_by_domain:
    urls.append(urls_by_domain[domain][0])

with open("../resources/urls.json", "w") as fp:
    json.dump(urls, fp)