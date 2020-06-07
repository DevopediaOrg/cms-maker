import sys
import time


sys.path.insert(0, "../")

from scrapy.crawler import CrawlerProcess
from scraper.spiders.contentscraper import ContentScraper
from scrapy.settings import Settings
import json
import logging


logging.basicConfig(level=logging.DEBUG)


class Validator:
    KEY_MATCHED_KEYS = "matched_keys"
    KEY_PARTIAL_MATCH = "partial_match"
    KEY_FULL_MATCH = "full_match"
    KEY_GOLD_MISSING_KEYS = "gold_missing_keys"
    KEY_GOLD = "gold"
    KEY_GENERATED = "generated"

    ADF_KEYS_TO_BE_NEGLECTED = ["url", "accessed_date"]

    def __init__(self, labeled_data_file, inputs_file, spider, adf_results_file):
        self.labelleled_data_file = labeled_data_file
        self.inputs_file = inputs_file
        self.spider = spider
        self.adf_results_file = adf_results_file
        self.adf_results = None

    def crawl(self):
        settings = Settings()
        # TODO Abhishek-P make this configurable
        settings.set("ITEM_PIPELINES", {"scraper.pipelines.ScraperPipeline": 100})
        process = CrawlerProcess(settings)
        process.crawl(self.spider)
        return process.start()

    def load_crawl_results(self):
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(self.adf_results_file, "r") as adf_results_fp:
            self.adf_results = json.load(adf_results_fp)
        logging.debug("Crawl results size {}".format(len(self.adf_results)))
        return self.adf_results

    def load_labelled_data(self):
        self.gold_results = None
        with open(self.labelleled_data_file, "r") as gold_results_fp:
            self.gold_results = json.load(gold_results_fp)
            print("Gold Results Size:", len(self.gold_results))
        return self.gold_results

    def validate_result(self, gold_reference, result_reference):
        # TODO Abhishek-P move this logic Format.ADF class
        result = dict()
        result["full_match"] = False
        result["partial_match"] = False
        result["matched_keys"] = list()
        result["gold_missing_keys"] = list()
        for key in result_reference:
            if key in gold_reference and key not in self.ADF_KEYS_TO_BE_NEGLECTED:
                # TODO Abhishek-P remove condition
                if gold_reference[key]:
                    if result_reference[key]:
                        if str(gold_reference[key]).lower() == str(result_reference[key]).lower():
                            result[self.KEY_MATCHED_KEYS].append(key)
                else:
                    result[self.KEY_GOLD_MISSING_KEYS].append(key)

        if len(result[self.KEY_MATCHED_KEYS]) == len(gold_reference):
            result[self.KEY_FULL_MATCH] = True

        elif len(result[self.KEY_MATCHED_KEYS]) > 0:
            result[self.KEY_PARTIAL_MATCH] = True
        result[self.KEY_GOLD] = gold_reference
        result[self.KEY_GENERATED] = result_reference
        return result

    def validate_results(self):
        results = dict()
        if self.gold_results and self.adf_results:
            for reference in self.adf_results:
                if reference in self.gold_results:
                # adf_result = self.adf_results[reference]
                # reference = reference.split("?")[0]
                    result = self.validate_result(self.gold_results[reference], self.adf_results[reference])
                    results[reference] = result
        return results

    def run(self):
        logging.debug("Starting Validator")
        # while not self.adf_results or len(self.adf_results) < 100:
        self.crawl()
        return;
        self.load_crawl_results()
        self.load_labelled_data()
        results = self.validate_results()
        count_full_matches = 0
        count_partial_matches = 0
        keys_stats_count = dict()
        avg_matched_keys_count = 0
        for ref in results:
            result = results[ref]
            logging.info("REFERENCE: {}".format(ref))
            gold = result[self.KEY_GOLD]
            gen = result[self.KEY_GENERATED]
            common_keys = set(gold.keys()).intersection(set(gen.keys()))
            columns = list(common_keys)
            gold_values = [str(gold[column]) for column in columns]
            gen_values = [str(gen[column]) for column in columns]
            values = [gold_values, gen_values]
            # tp.table(values, columns)
            logging.info("MATCHED_KEYS: {}".format(result[self.KEY_MATCHED_KEYS]))
            if result[self.KEY_FULL_MATCH]:
                count_full_matches += 1
                avg_matched_keys_count += len(result[self.KEY_MATCHED_KEYS])
            elif result[self.KEY_PARTIAL_MATCH]:
                count_partial_matches += 1
                avg_matched_keys_count += len(result[self.KEY_MATCHED_KEYS])
            for key in result[self.KEY_MATCHED_KEYS]:
                if not key in keys_stats_count:
                    keys_stats_count[key] = 0

                keys_stats_count[key] += 1
        if len(results) > 0:
            avg_matched_keys_count = avg_matched_keys_count / len(results)
        logging.info("TOTAL: {}".format(len(results)))
        logging.info("FULL MATCHES: {}".format(count_full_matches))
        logging.info("PARTIAL MATCHES: {}".format(count_partial_matches))
        logging.info("AVG MATCHED KEYS: {}".format(avg_matched_keys_count))
        logging.info("KEY_MATCHED STATUS {}".format(keys_stats_count))


if __name__ == "__main__":
    validator = Validator("../resources/url_references.json", "../urls.json", ContentScraper,
                          "../resources/adf_results.json")
    validator.run()
