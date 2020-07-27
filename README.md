# Overview

Given a URL, parse the content at that URL and generate a reference in Chicago Manual of Style (CMS) format. The two main Python packages used are:
* `scrapy`: to web scrape the URL
* `beautifulsoup4`: to parse the HTML content obtained from scraping

To install Python dependencies, run `pip install -r requirements.txt`

To invoke the scraping process and rest of the processing pipeline, call `scrapy crawl content`. 

The tool reads a list of URLs from file of default name `urls.json`. This file should reside in the root project folder. Here's an example input file:
```
[
    "https://towardsdatascience.com/topic-modeling-and-latent-dirichlet-allocation-in-python-9bf156893c24",
    "https://www.analyticsvidhya.com/blog/2016/08/beginners-guide-to-topic-modeling-in-python/",
    "https://www.kdnuggets.com/2016/07/text-mining-101-topic-modeling.html",
    "https://www.tidytextmining.com/",
    "https://www.oreilly.com/library/view/text-mining-with/9781491981641/ch06.html",
    "https://monkeylearn.com/blog/introduction-to-topic-modeling/",
    "https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/",
    "https://medium.com/nanonets/topic-modeling-with-lsa-psla-lda-and-lda2vec-555ff65b0b05",
    "https://arxiv.org/abs/1711.04305",
    "https://nlpforhackers.io/topic-modeling/",
    "https://www.youtube.com/watch?v=NYkbqzTlW3w",
    "https://en.wikipedia.org/wiki/Topic_model",
    "https://www.aclweb.org/anthology/W04-3252/"
]
```


# Chicago Manual of Style

CMS comes in two formats. We have adopted the [Author-Date format](http://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-2.html).

At Devopedia, we might have customized the format a little bit to suit our purposes. Examples of how we use CMS are on the [Author Guidelines](https://devopedia.org/site-map/author-guidelines?good-bad-examples) page of Devopedia main site. Go to the *References* sub-section of *Good & Bad Examples* section.

![Reference Example](https://devopedia.org/images/misc/ReferenceExample.svg)


# Developer Notes

These notes are temporary and likely to be deleted once code is refactored.

- pre_process.bat calls article_sql_to_cms.py and clean_references.py:
  - article_sql_to_cms.py
    - read from DB cms_maker, extract references, use regex to get fields
    - saved into references.json {title: ref}
  - clean_references.py
    - remove None fields in references
    - updates references.json
  - both scripts pickle references.json is pickled as references.pkl

- CMS.Format.AuthorDateFormat:
  - called from html_scraper.py, article_sql_to_cms.py, and gold_results_stats.py
  - simply creates placeholders for the fields: init by callers

- traversal_rule_identifier.py:
  - defines TraversalRule class
  - used by cms_maker.py, html_scraper.py, and pipelines.py

- Standalone scripts:
  - cms_maker.py:
    - defines classes AuthorTraversalRules, FindAuthorWithTraversal, FindAuthor
    - code can be simplified
  - convert_references_to_url_based_dict.py:
    - references.json reformatted and saved into url_references.json {url: ref}
    - URLs saved into urls.json
    - url_references.json considered as gold results
  - validate.py: uses url_references.json and adf_results.json
  - collect_urls_by_domain.py:
    - reads urls.json and saves urls_by_domains.json: {domain: [urls]}
  - pick_from_each_domains.py:
    - reads urls_by_domains.json
    - picks first URL of each domain and saves into urls.json
  - gold_results_stats.py:
    - reads url_references.json and prints stats
    - stats are count of presence of fields
    - also counting how many refs are PDFs
  - partition_urls.json.py:
    - reads urls.json and saves urls-*.json files (batches of 20 URLs)
    - simplify as l[i:i+n] for i in range(0, len(l), n)]
  - pick_by_subdomain.py:
    - reads url_references.json and picks URLs of specific TLD domains
    - TLD eg. medium.com; domain eg. www.medium.com
    - saves two files domain_url_references.json {tld: [refs]} and picked_references.json [domain]
  - pick_random_references.json.py:
    - reads references.json and picks some random entries
    - poor code: can be a lot simpler
  - to_title_references.py:
    - reads references.json and saves into title_references.json {title: url}
