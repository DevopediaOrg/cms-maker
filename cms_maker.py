import urllib3
import traversal_rule_identifier
from bs4 import BeautifulSoup
import json
import tldextract
import certifi
import ssl

ssl_context = ssl.SSLContext()
ssl_context.load_verify_locations(certifi.where())
http = urllib3.PoolManager(ssl_context=ssl_context)

class AuthorTraversalRules:
    persistence_type = "json"

    def __init__(self, filename):
        self.filename = filename
        self.author_traversal_rules = dict()
        self.load_author_traversal_rules()

    def load_author_traversal_rules(self):
        with open(self.filename, "r") as fp:
            self.author_traversal_rules =  json.load(fp)

    def get_author_traversal_for_url(self, url):
        extract_result = tldextract.extract(url)
        host_url = extract_result.registered_domain
        if host_url in self.author_traversal_rules:
            return self.author_traversal_rules[host_url]
        return None

class FindAuthorWithTraversal:

    def __init__(self, url, author_traversal_rule_for_site):
        self.url = url
        self.author_traversal_rule = author_traversal_rule_for_site
        self.page_content = None

    def load_page_content(self):
        self.page_content = http.request('GET', self.url).data

    def get_author(self):
        self.load_page_content()
        soup = BeautifulSoup(self.page_content, 'lxml')
        soup = BeautifulSoup(soup.prettify('utf-8'), 'lxml')
        t = traversal_rule_identifier.TraversalRule(soup, None, self.author_traversal_rule)
        return t.get_author_from_traversal()


class FindAuthor:
    domain_traversal_file = "./resources/domain_traversal_rules-500.json"
    domain_traversal = AuthorTraversalRules(domain_traversal_file)

    def __init__(self, url):
        self.url = url
        extracted = tldextract.extract(url)
        site = extracted.registered_domain
        self.find_author = FindAuthorWithTraversal(self.url, self.domain_traversal.author_traversal_rules[site])

    def get_author(self):
        return self.find_author.get_author()

if __name__ == "__main__":
    print(FindAuthor("https://www.linkedin.com/pulse/automating-user-creation-aws-sftp-service-transfer-arjun-dandagi/").get_author())