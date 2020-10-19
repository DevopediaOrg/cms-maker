# Overview

Given a document, parse the content and generate a reference in Chicago Manual of Style (CMS) format. Most document are in HTML, text, PDF, or PPT formats.

These documents are in fact mentioned in [Devopedia](https://devopedia.org) published articles, in sections References and Further Reading of each article. Other packages (not linked to this codebase) have already done two things:
- Queried Devopedia database to extract the URLs in each article, and saved the exported data in a JSON file (`*.json`).
- Crawled the web for these URLs, saved each document content, and saved metadata in a JSON Lines file (`*.jl`).

Thus, inputs to this codebase are Devopedia article content, documents pertaining to URLs, and metadata about crawled URLs.

To install Python dependencies, run `pip install -r requirements.txt`


# Chicago Manual of Style

CMS comes in two formats. We have adopted the [Author-Date format](http://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-2.html).

At Devopedia, we might have customized the format a little bit to suit our purposes. Examples of how we use CMS are on the [Author Guidelines](https://devopedia.org/site-map/author-guidelines?good-bad-examples) page of Devopedia main site. Go to the *References* sub-section of *Good & Bad Examples* section.

![Reference Example](https://devopedia.org/images/misc/ReferenceExample.svg)


# Developer Notes

These notes are temporary and likely to be deleted once code is refactored.

- Summary
  - Extract ground truth: article_sql_to_cms.py
  - Training: html_scraper.py, pipelines.py
  - Inference: cms_maker.py
  - Rules: domain_traversal_rules-500.json
- pre_process.bat calls article_sql_to_cms.py and clean_references.py:
  - article_sql_to_cms.py
    - read from DB cms_maker, extract references, use regex to get fields
    - saved into references.json {title: ref}
    - refactor this code to read from Devopedia article JSON file instead
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
    - cms_maker.py: given content and rules, extract author
    - html_scraper.py: given content, find possible candidates
    - pipelines.py: given author name (ground truth via regex) and candidates, pick matching candidate and rule

- pipelines.py:
  - called by scrapy for each item crawled
  - writes nothing to output files adf_results.json and results.json
  - writes to files url_author_candidates.json and domain_traversal_rules-500.json
  - file url_author_candidates.json is empty

- Standalone scripts:
  - cms_maker.py:
    - defines classes AuthorTraversalRules, FindAuthorWithTraversal, FindAuthor
    - code can be simplified
    - extracts only author name for now, doesn't actually return in CMS format
    - reads file domain_traversal_rules-500.json, file created in pipelines.py
    - doesn't handle domain that doesn't have a rule
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
    
- Notebooks
  - cms-traversal-rules.py
    -  Does not work! : Notebook written to wrap the validate.py script to utilize Google Colab infra structure for generating the author traversal rules from gold data
