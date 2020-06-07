# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
import tldextract
sys.path.insert(0, "../")
from CMS import Format
from traversal_rule_identifier import TraversalRule
import json
import logging

from traversal_rule_identifier import TraversalRule
logging.basicConfig(level=logging.INFO)
AUTHOR_CANDIDATES_FILE_PREFIX = "author-candidates-"

class ScraperPipeline(object):
    def open_spider(self, spider):
        logging.debug("Opening Spider")
        self.adf_file = open("../resources/adf_results.json", "w")
        self.items_file = open("../resources/results.json", "w")
        self.author_candidates_file = open("../resources/url_author_candidates.json", "w")
        self.url_references = dict()
        self.results = dict()
        self.items = []
        self.author_candidates = dict()
        self.traversal = dict()
        self.traversal_rule_file = open("../resources/domain_traversal_rules.json", "w")
        with open("../resources/url_references.json", "r") as fp:
            self.url_references = json.load(fp)

    def close_spider(self, spider):
        # logging.debug("Closing Spider and dumping {}".format(self.results))
        json.dump(self.results, self.adf_file, cls=Format.MyEncoder)
        # json.dump(self.items, self.items_file, cls=Format.MyEncoder)
        logging.info("author candidates {}".format(self.author_candidates))
        json.dump(self.author_candidates, self.author_candidates_file)
        json.dump(self.traversal, self.traversal_rule_file)
        self.items_file.close()
        self.adf_file.close()
        self.author_candidates_file.close()

    def process_item(self, item, spider):
        if item["CMS-ADF"]:
            adf = item["CMS-ADF"]
            self.results[adf.url] = adf
            if "CANDIDATE_AUTHORS" in item:
                logging.debug("Dumping Candidate Authors for {}".format(adf.url))
                self.author_candidates[adf.url] = item["CANDIDATE_AUTHORS"]

            if get_domain(adf.url) not in self.traversal and self.author_candidates and self.url_references and adf.url in self.url_references and adf.url in self.author_candidates :
                reference = self.url_references[adf.url]
                if reference['author_name']:
                    tr = TraversalRule(None, reference['author_name'], None)
                    tr.candidates = self.author_candidates[adf.url]
                    tr.pick_traversal_from_author()
                    if tr.traversal_rule:
                        self.traversal[get_domain(adf.url)] = tr.traversal_rule

            logging.debug("Traversal rule {}".format(self.traversal))

        self.items.append(item)
        return item

def get_domain(url):
    extracted = tldextract.extract(url)
    return extracted.registered_domain
