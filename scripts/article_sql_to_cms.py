# import peewee
# from peewee import *
# db = MySQLDatabase('cms_maker')
#
# class Article(Model):
#
import sys
sys.path.insert(0, '../')
from CMS import Format
import re
import mysql.connector
import json
import logging
from mysql.connector import Error
import pickle

logging.basicConfig(level=logging.INFO)


class ArticleReader:
    def get_article_contents(self):
        try:
            conn = mysql.connector.connect(host='localhost',
                                           database='cms_maker',
                                           user='root')
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("select title, introtext from fkd5g_content;")
                record = cursor.fetchall()
        except Error as e:
            pass
        finally:
            # closing database connection.
            if (conn.is_connected()):
                cursor.close()
                conn.close()
        return record


class ReferenceExtractor:
    REFERENCES_SECTION_HEADER = "\r\n\r\nReferences\r\n----------\r\n\r\n"

    REFERENCE_REGEX = "\[.*?\]\(.*?\)\r\n"

    CMS_AUTHOR_YEAR_TITLE_REGEX = "\[(?P<authors>.*?)\.\W*(?P<year>[0-9]{4}[a-z]?)\.\W*(?P<title>\".*\")\.?.*"

    # Date can be internal like May17-25, or  Febraury 19, 2017
    CMS_DATE_PUB_UPDATED_ACCESSED_URL_REGEX = ",?(?P<date>[A-Za-z]+\W([0-2][0-9]|[3][01]))?(\.\W*)?(\,\W*)?(?P<date_updated>(Updated?\W[a-zA-Z]+\W+([0-9]{1,2}|([0-2]?[0-9]|[3]?[01])-([0-2]?[0-9]|[3]?[01]))|[0-9]{4}-[0-9]{2}-[0-9]{2})?)(\.\W*)?(?P<access_date>(Accessed|Retrieved)\W*[0-9]{4}-[0-9]{2}-[0-9]{2})(\.\W*)?\]\.*?\((?P<url>.*\??)\)"

    CMS_REGEX = ".*?(?P<details>.*?)?(\.)?\W*?(?P<publisher>.*?)\,.*?"

    def __init__(self, articles):
        super()
        self.articles = articles
        self.references = dict()
        self.extract_references()

    def get_references_content(self, title, article_text):
        # since references is the last section extracting the text after the section header
        ref_text = article_text[article_text.find(self.REFERENCES_SECTION_HEADER):]
        return ref_text

    def extract_reference_texts(self, reference_text):
        refs = re.findall(self.REFERENCE_REGEX, reference_text)
        return refs

    def parse_ref(self, ref_text):
        match1 = re.search(self.CMS_AUTHOR_YEAR_TITLE_REGEX, ref_text)

        ref = Format.AuthorDateFormat();
        if match1:
            if match1.group('authors'):
                ref.author_name = match1.group('authors')
            ref.year_of_publication = match1.group('year')
            ref.title = match1.group('title')
            ref_text = ref_text[match1.end('title'):]

        match3 = re.search(self.CMS_DATE_PUB_UPDATED_ACCESSED_URL_REGEX, ref_text)
        if match3:
            # Didn't fit the format
            if match3.group('date'):
                ref.date_of_publication = match3.group('date')
                ref_text = ref_text[:match3.start('date')]
            else:
                ref_text = ref_text[:match3.start('date_updated')]
            ref.date_updated = match3.group('date_updated')
            ref.access_date = match3.group('access_date')
            if not ref.year_of_publication:
                # TODO Abhishek-P extract year from access_date
                pass
            if not ref.date_of_publication:
                # TODO Abhishek-P extract date from access_date
                pass
            ref.url = match3.group('url')
            if ref.url.find("?"):
                values = ref.url.split("?")
                ref.url = values[0]
        match = re.search(self.CMS_REGEX, ref_text)
        if match:
            if match.group('details'):
                ref.details = match.group('details')
            if match.group('publisher'):
                ref.publisher_name = match.group('publisher')
                if not ref.author_name:
                    ref.author_name = ref.publisher_name
        if not match1 and not match3 and match:
            return None
        return ref

    def extract_references(self):
        logging.debug("Extracting references from {} articles".format(len(self.articles)))
        for article in self.articles:
            refs_content = self.get_references_content(article[0], article[1])
            ref_texts = self.extract_reference_texts(refs_content)
            logging.debug(ref_texts)
            refs = [self.parse_ref(ref) for ref in ref_texts]
            self.references[article[0]] = refs
            logging.debug("extracted {} refs {} for article".format(len(refs), refs, article[0]))

articles = ArticleReader().get_article_contents()
refExtractor = ReferenceExtractor(articles)
references = refExtractor.references
logging.info("Total Articles: {}".format(len(references)))
with open("../resources/references.pkl", "wb") as dump_file:
    pickle.dump(references, dump_file)

with open("../resources/references.json", "w") as dump_file:
    json.dump(references, dump_file, cls=Format.MyEncoder)
