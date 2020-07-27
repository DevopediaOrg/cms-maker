import json
from tldextract import tldextract
import logging
logging.basicConfig(level=logging.DEBUG)
urls = None
urls_by_domains = dict()
with open("../resources/urls.json", "r") as fp:
    urls = json.load(fp)

for url in urls:
    logging.debug("url {}".format(url))
    if not url:
        continue
    extract_result = tldextract.extract(url)
    host_url = extract_result.registered_domain
    if host_url not in urls_by_domains:
        urls_by_domains[host_url] = list()
    urls_by_domains[host_url].append(url)

with open("../resources/urls_by_domains.json", "w") as fp:
    json.dump(urls_by_domains, fp)

