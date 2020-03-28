# import peewee
# from peewee import *
# db = MySQLDatabase('cms_maker')
#
# class Article(Model):
#

import CMS
import re
import mysql.connector
import json
from mysql.connector import Error
import pickle

PRINT = False


def local_print(*values):
    if PRINT:
        print(values)


def get_article_contents():
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='cms_maker',
                                       user='root')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("select title, introtext from fkd5g_content;")
            record = cursor.fetchall()
    except Error as e:
        local_print("Print your error msg", e)
    finally:
        # closing database connection.
        if (conn.is_connected()):
            cursor.close()
            conn.close()
    return record


REFERENCES_SECTION_HEADER = "\r\n\r\nReferences\r\n----------\r\n\r\n"


def get_references_content(title, article_text):
    local_print("extracting reference text for article", title)
    # since references is the last section extracting the text after the section header
    ref_text = article_text[article_text.find(REFERENCES_SECTION_HEADER):]
    local_print(len(ref_text))
    return ref_text


REFERENCE_REGEX = "\[.*?\]\(.*?\)\r\n"


def extract_reference_texts(reference_text):
    refs = re.findall(REFERENCE_REGEX, reference_text)
    local_print(len(refs))
    return refs


# TODO abhip make details, publisher, date distinct
# TODO abhip authors is optional?
CMS_REGEX = "\[\
(?P<authors>.*?)(\.\W*)\
(?P<year>[0-9]{4})\.\W*\
(?P<title>\".*\")\.?\W*\
(?P<details>.*?)?(\.\W*)?\
(?P<publisher>.*?)?(\,\W*)?\
(?P<date>.*?)?(\,\W*)?\
(?P<date_updated>[a-zA-Z]*\W+[0-9]{2}?)(\.\W*)?\
(?P<access_date>Accessed.*?)(\.\W*)?\
\]\
.*?\((?P<url>.*?)\)"


def parse_ref(ref_text):
    local_print(ref_text)
    match = re.search(CMS_REGEX, ref_text)
    ref = CMS.AuthorDateFormat();
    if not match:
        # Didn't fit the format
        return None
    if match.group('authors'):
        local_print(match.group('authors'))
        ref.author_name = match.group('authors')
    local_print(match.group('year'))
    ref.year_of_publication = match.group('year')
    local_print(match.group('title'))
    ref.title = match.group('title')
    if match.group('details'):
        local_print(match.group('details'))
        ref.details = match.group('details')
    if match.group('publisher'):
        local_print(match.group('publiser'))
        ref.publisher_name = match.group('publisher')
    if match.group('date'):
        local_print(match.group('date'))
        ref.date_of_publication = match.group('date')
    local_print(match.group('date_updated'))
    ref.date_updated = match.group('date_updated')
    local_print(match.group('access_date'))
    ref.access_date = match.group('access_date')
    local_print(match.group('url'))
    ref.url = match.group('url')
    return ref


#
# # Get Articles
# # # Get Reference section of Articles
# # refs_content = get_references_content(record[0][0], record[0][1])
# #
# # # Extract text for each reference
# # ref_texts = extract_reference_texts(refs_content)
# #
# # # Convert Ref to CMS object
# # local_print(parse_ref(ref_texts[0]))
# record = get_article_contents()
# local_print("articles:", len(record))
# references = {}
# for article in record:
#     refs_content = get_references_content(article[0], article[1])
#     ref_texts = extract_reference_texts(refs_content)
#     refs = [parse_ref(ref) for ref in ref_texts]
#     references[article[0]] = refs
#
# print(len(references))
# with open("resources/references.pkl", "wb") as dump_file:
#     pickle.dump(references, dump_file)

with open("resources/references.pkl", "rb") as dump_file:
    references = pickle.load(dump_file)

with open("resources/references.json", "w") as dump_file:
    json.dump(references, dump_file,cls=CMS.MyEncoder)
