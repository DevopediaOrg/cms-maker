# import peewee
# from peewee import *
# db = MySQLDatabase('cms_maker')
#
# class Article(Model):
#

from CMS import Format
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

CMS_AUTHOR_YEAR_TITLE_REGEX = "\[\
(?P<authors>.*?)\.\
\W* \
(?P<year>[0-9]{4})\.\
\W*\
(?P<title>\".*\")\.?.*"

# Date can be internal like May17-25, or  Febraury 19, 2017
CMS_DATE_PUB_UPDATED_ACCESSED_URL_REGEX = ",?\
(?P<date>[A-Za-z]+\W([0-2][0-9]|[3][01]))?(\.\W*)?\
(\,\W*)?\
(?P<date_updated>(Updated?\W[a-zA-Z]+\W+[0-9]{2}|[0-9]{4}-[0-9]{2}-[0-9]{2})?)(\.\W*)?\
(?P<access_date>(Accessed|Retrieved)\W*[0-9]{4}-[0-9]{2}-[0-9]{2})(\.\W*)?\
\]\
.*?\((?P<url>.*?)\)"

CMS_REGEX = ".*?\
(?P<details>.*?)?(\.)?\W*?\
(?P<publisher>.*?)\,.*?"

def parse_ref(ref_text):
    local_print(ref_text)
    match1 = re.search(CMS_AUTHOR_YEAR_TITLE_REGEX, ref_text)

    ref = Format.AuthorDateFormat();
    if match1:
        if match1.group('authors'):
            local_print(match1.group('authors'))
            ref.author_name = match1.group('authors')
        local_print(match1.group('year'))
        ref.year_of_publication = match1.group('year')
        local_print(match1.group('title'))
        ref.title = match1.group('title')
        ref_text = ref_text[match1.end('title'):]

    match3 = re.search(CMS_DATE_PUB_UPDATED_ACCESSED_URL_REGEX, ref_text)
    if match3:
        # Didn't fit the format
        if match3.group('date'):
            local_print(match3.group('date'))
            ref.date_of_publication = match3.group('date')
            ref_text = ref_text[:match3.start('date')]
        else:
            ref_text = ref_text[:match3.start('date_updated')]
        local_print(match3.group('date_updated'))
        ref.date_updated = match3.group('date_updated')
        local_print(match3.group('access_date'))
        ref.access_date = match3.group('access_date')
        local_print(match3.group('url'))
        ref.url = match3.group('url')
    match = re.search(CMS_REGEX, ref_text)
    if match:
        if match.group('details'):
            local_print(match.group('details'))
            ref.details = match.group('details')
        if match.group('publisher'):
            local_print(match.group('publisher'))
            ref.publisher_name = match.group('publisher')
    if not match1 and not match3 and match:
        return None
    return ref


#
# Get Articles
# # Get Reference section of Articles
# refs_content = get_references_content(record[0][0], record[0][1])
#
# # Extract text for each reference
# ref_texts = extract_reference_texts(refs_content)
#
# # Convert Ref to CMS object
# local_print(parse_ref(ref_texts[0]))
record = get_article_contents()
local_print("articles:", len(record))
references = {}
for article in record:
    refs_content = get_references_content(article[0], article[1])
    ref_texts = extract_reference_texts(refs_content)
    refs = [parse_ref(ref) for ref in ref_texts]
    references[article[0]] = refs

print(len(references))
with open("../resources/references.pkl", "wb") as dump_file:
    pickle.dump(references, dump_file)

# with open("../resources/references.pkl", "rb") as dump_file:
#     references = pickle.load(dump_file)

with open("../resources/references.json", "w") as dump_file:
    json.dump(references, dump_file, cls=Format.MyEncoder)
