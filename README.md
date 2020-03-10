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
