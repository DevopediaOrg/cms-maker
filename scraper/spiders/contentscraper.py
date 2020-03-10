''' Module to scrape content from web pages. '''

import os.path
import json
import hashlib

import scrapy

import html_scraper


class ContentScraper(scrapy.Spider):
    ''' Spider to scrape content from a list of URLs.
        URLs are read from a file named urls.json.
    '''
    name = "content"
    urlfile = "urls.json"

    def start_requests(self):
        # Expected to be passed from command line
        if not self.urlfile:
            raise scrapy.exceptions.CloseSpider('No valid URL JSON file specified.')

        # Read URLs from a JSON file
        with open(self.urlfile) as fin:
            urls = json.load(fin)

        if not urls or not isinstance(urls, list):
            raise scrapy.exceptions.CloseSpider('No valid URLs seen in JSON file.')

        # Init the HTML scraper
        self.hscp = html_scraper.HtmlScraper()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        fname = self.get_fname(response.url)
        with open(fname, 'wb') as fout:
            fout.write(response.body)

        content = self.hscp.scrape({
            'link' : response.url,
            'fullcontent' : response.body }, toPrint=True)
        content.update({'Filename': fname})

        yield content

    @classmethod
    def get_fname(cls, url):
        ''' Given the URL return a suitable filename. '''
        hexdig = hashlib.sha256(url.encode('utf-8')).hexdigest()
        return ".cache/{}.htm".format(hexdig)
