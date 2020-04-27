# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys

sys.path.insert(0, "../")
from CMS import Format
import json
import logging

logging.basicConfig(level=logging.DEBUG)


class ScraperPipeline(object):
    def open_spider(self, spider):
        logging.debug("Opening Spider")
        self.adf_file = open("../resources/adf_results.json", "w")
        self.items_file = open("../resources/results.json", "w")
        self.results = dict()
        self.items = []

    def close_spider(self, spider):
        logging.debug("Closing Spider and dumping {}".format(self.results))
        json.dump(self.results, self.adf_file, cls=Format.MyEncoder)
        json.dump(self.items, self.items_file, cls=Format.MyEncoder)
        self.items_file.close()
        self.adf_file.close()

    def process_item(self, item, spider):
        if item["CMS-ADF"]:
            adf = item["CMS-ADF"]
            self.results[adf.url] = adf
        self.items.append(item)
        return item
