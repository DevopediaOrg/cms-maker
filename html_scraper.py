from bs4 import BeautifulSoup
import io
import copy
import feedparser
import inspect
import iso8601
import re
import time
import datetime
from urllib.parse import urlparse, urlunparse, urlsplit
import sys
import CMS

class HtmlScraper(object):    

    fields = [
        'Url',
        'Title',
        'SrcDate',
        'AuthorSite',
        'Image',
        'FirstText'
    ]
    
    tagCategories = {
        'unlikely' : '(icon-white|whitepaper|webcast|podcast|webinar|combx|comment|community|disqus|extra|foot|menu|remark|rss|shoutbox|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter)',
        'maybe' : 'and|article|body|column|main|shadow',
        'positive' : 'article|body|content|entry|hentry|main|page|pagination|post|text|blog|story',
        'negative' : 'combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget',
        'extraneous' : 'print|archive|comment|discuss|e[\-]?mail|share|reply|all|login|sign|single',
        'divToPElements' : '<(a|blockquote|dl|div|img|ol|p|pre|table|ul)',
        'replaceBrs' : '(<br[^>]*>[ \n\r\t]*){2,}',
        'replaceFonts' : '<(\/?)font[^>]*>',
        'trim' : '^\s+|\s+$',
        'normalize' : '\s{2,}',
        'killBreaks' : '(<br\s*\/?>(\s|&nbsp;?)*){1,}',
        'videos' : 'http:\/\/(www\.)?(youtube|vimeo)\.com',
        'skipFootnoteLink' : '^\s*(\[?[a-z0-9]{1,2}\]?|^|edit|citation needed)\s*$',
        'nextLink' : '(next|weiter|continue|>([^\|]|$)|&raquo;?([^\|]|$))',
        'prevLink' : '(prev|earl|old|new|<|&laquo;?)'
    }

    sitemap = {
        'www.powersystemsdesign.com' : {'Image':('class_','mg-inner','src')},
        'kk.org' : {'Image':('class_','entryleadimage','src')},
        'www.mondaynote.com' : {'Image':('class_','pf-content','src')},
        'designthinking.ideo.com' : {'Image':('class_','entry-content clearfix','src')},
        'www.appliancist.com' : {'Image':('id','entry','src')},
        'thecityfix.com' : {'Image':('class_','post-entry','src')},
        'www.raspberrypi.org' : {'Image':('class_','entry-content','src')},
        'gsaauctions.gov' : {'Image':('class_','fullsize','src')},
        'blog.arduino.cc' : {'Image':('class_','entry','src')},
        'www.theatlantic.com' : {'Image':('class_','article-content','src')},
        'www.inc.com' : {'Image':('id','articleheaderimage','src')},
        'readwrite.com' : {'Image':('itemprop','articleBody','src')},
        'www.gizmag.com' : {'Image':('id','content','src')},
        'www.dailywireless.org' : {'Image':('class_','entry','src')},
        'blog.3g4g.co.uk' : {'Image':('class_','post-body entry-content','src')},
        'machinedesign.com' : {'Image':('id','content','src')},
        'www.aviationtoday.com' : {'Image':('id','content-main','src')},
        'www.designnews.com' : {'Image':('class_','docimage','src'), 'Author':('class_', 'gray', 'author_section.b.text.split()[0]')},
        'processengineering.theengineer.co.uk' : {'Image':('class_','inlineFull','src')},
        'www.eurekamagazine.co.uk' : {'Image':('class_','centreImage','src')},
        'headstart.in' : {'Image':('id','main','src')},
        'medianama.com' : {'Image':('id','content','src')},
        'domain-b.com' : {'Image':('class_','maintext','src')},
        'dnaindia.com' : {'Image':('class_','content-image','src')},
        'zeenews.india.com' : {'Image':('class_','article-image-gh','src')},
        'googleblog.blogspot.co.uk' : {'Image':('class_','post-body','src')},
        'www.labnol.org' : {'Image':('class_','post-content','src')},
        'semanticweb.com' : {'Image':('class_','postContent','src')},
        'blog.codinghorror.com' : {'Image':('class_','post-content','src')},
        'www.medgadget.com' : {'Image':('class_','post-content','src')},
        'seroundtable.com' : {'Image':('id','content','src')},
        'techcircle.vccircle.com' : {'Image':('id','main','src')},
        'ianslive.in' : {'Image':('class_','landingstory','src')},
        'indiatoday.intoday.in' : {'Image':('id','storyleft','src')},
        'www.flightglobal.com' : {'Image':('class_','rbi-art-body','src')},
        'www.slashgear.com' : {'Image':('class_','postimage','src')},
        'www.joelonsoftware.com' : {'Image':('class_','sideimg','src')},
        'bits.blogs.nytimes.com' : {'Image':('class_','image','src')},
        'www.scientific-computing.com' : {'Image':('id','content','src')},
        'bgr.com' : {'Image':('class_','article-content','src')},
        'abcnews.go.com' : {'Image':('id','storyText','src')},
        'www.digitaltrends.com' : {'Image':('class_','wrap','src')},
        'www.latimes.com' : {'Image':('class_','trb_embed_media','data-baseurl')},
        'thedailywtf.com' : {'Image':('class_','ArticleBody','src')},
        'www.washingtonpost.com' : {'Image':('id','article-body','src')},
        'www.creativeapplications.net' : {'Image':('id','postblock','src')},
        'online.wsj.com' : {'Author':('name', 'author','author[\'content\']')},
        'gigaom.com' : {'Author':('name', 'author', 'author[\'content\']')},
        'www.zdnet' : {'Author': ('rel', 'author', 'author.string.strip()')},
        'www.datacenterknowledge.com' : {'Author':('itemprop','name','author.string.strip()')},
        'consumerist.com' : {'Author':('rel','author','author[\'title\']')},
        'wwlp.com' : {'Author':('class','byline','author[0].string.strip()')},
        'woodtv.com' : {'Author':('class','byline','author[0].string.strip()')},
        'www.techweekeurope.co.uk' : {'Author':('rel','author','author[0].string.strip()')},
        'www.autonews.com' : {'Author':('rel','author','author[0].b.string.strip()')},
        'www.spyghana.com' : {'Author':('class','author-name','author[0].string.strip()')},
        'michronicleonline.com' : {'Author':('class','author-name author vcard', 'author[0].get_text().strip()')},
        'www.tennessean.com' : {'Author':('class','asset-metabar-author','author[0].get_text().strip()')},
        'www.gloucestershireecho.co.uk' : {'Author':('class','author','author[0].a.get_text().strip()')},
        'www.india.com' : {'Author':('class','author vcard', 'author[0].a.get_text().strip()')},
        'www.inserbia.info' : {'Author':('class','td-author-name','author[0].a.get_text().strip()')},
        'www.wallstreetscope.com' : {'Author':('class','td-block-author','author[0].a.get_text().strip()')},
        'agwired.com': {'Author':('class','x-icon-pencil','author[0].get_text().strip()')},
        'recode.net' : {'Author':('class','author','author[0].get_text().strip()')},
        'www.asianscientist.com' : {'Author':('rel','author','author[0].get_text().strip()')},
        'www.cambridge-news.co.uk' : {'Author':('class','author','author[0].a.get_text().strip()')},
        'www.newsleader.com' : {'Author':('class','asset-metabar-author','author[0].get_text().strip()')},
        'blogs.vancouversun.com' : {'Author':('rel','author','author[0].get_text().strip()')},
        'venturebeat.com' : {'Author':('class','url fn','author[0].get_text().strip()')},
        'www.greenbaypressgazette.com' : {'Author':('class','asset-metabar-author asset-metabar-item','author[0].get_text().strip()')},
        'www.zdnet.com' : {'Author':('rel','author','author[0].get_text().strip()')},
        'uk.businessinsider.com' : {'Author':('rel','author','author[0].get_text().strip()')},
        'uk.citizen-times.com' : {'Author':('class','asset-metabar-author asset-metabar-item','author[0].a.get_text().strip()')},
        'www.citizen-times.com' : {'Author':('class','asset-metabar-author asset-metabar-item','author[0].a.get_text().strip()')},
        'www.seroundtable.com' : {'Author':('rel','author','author[1].get_text().strip()')},
        'www.wsj.com' : {'Author':('class','name','author[0].get_text().strip()')},
        'www.tallahassee.com' : {'Author':('itemprop','name','author[0].get_text().strip()')},
        'boston.cbslocal.com' : {'Author':('class','subtitle','author[11].get_text().strip()')},
        'www.nytimes.com' : {'Author':('class','byline-author','author[0].get_text().strip()')},
        'www.desertsun.com' : {'Author':('class','asset-metabar-author asset-metabar-item','author[0].a.get_text().strip()')},
        'www.dailymail.co.uk' : {'Author':('class','author','author[0].get_text().strip()')},
        'bostinno.streetwise.co' : {'Author':('rel','author','author[0].get_text().strip()')},
        'www.edsurge.com' : {'Author':('class','author-image','author[0].parent.parent.strong.a.get_text().strip()')},
        'www.democratandchronicle.com' : {'Author':('class','asset-metabar-author asset-metabar-item','author[0].get_text().strip()')}
    }


    #--------------------------------------------------------------------
    def __init__(self):
        self.page_count = 0 # total parsed
        self.news_items = [] # items accepted

        self.parsely_count = 0
        self.microdata_count = 0
        self.opengraph_count = 0
    
    
    #--------------------------------------------------------------------
    def log(self, text):
        pass


    #--------------------------------------------------------------------
    def print_articles(self, withText=True):
        for item in self.news_items:
            self.__print_article_item(item, withText)

        
    #--------------------------------------------------------------------
    def print_article(self, inType, value, withText=True):
        if inType=='url':
            self.__print_article_item(self.get_article(value), withText)
        elif inType=='item':
            self.__print_article_item(value, withText)
        else:
            self.log("Warn: Unsupported type in method %s(): %s. Skipping ..." % (inspect.stack()[0][3], inType))


    #--------------------------------------------------------------------
    def __print_article_item(self, item, withText=True):
        for key in item:
            if withText or not withText and key!='FullText':
                try: #re.search(r'^(FirstText|FullText|Title)$',key)
                    if item[key]:
                        print('%12s : %s' % (key, item[key].encode('utf-8')))
                    else:
                        print('%12s : %s' % (key, item[key]))
                except UnicodeDecodeError as e:
                    print('%12s : %s' % (key, item[key]))
                except UnicodeEncodeError as e:
                    self.log("Warn: UnicodeEncodeError: %s. Skipping ..." % (str(e)))

        
    #--------------------------------------------------------------------
    def print_stats(self):
        print('Page count : %d' % (self.page_count))
        print('Parsely count : %d' % (self.parsely_count))
        print('Microdata count : %d' % (self.microdata_count))
        print('Opengraph count : %d' % (self.opengraph_count))

    
    #--------------------------------------------------------------------
    def get_article(self, url):
        for item in self.news_items:
            if 'Url' in item and item['Url']==url:
                return item
        return None
        

    #--------------------------------------------------------------------
    def make_cms(self, article):
        try:
            monthdate, year = [x.strip() for x in article['SrcDate'].split(',')]
        except:
            monthdate = year = None
        today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        cms_obj = CMS.AuthorDateFormat()
        cms_obj.title = article['Title']
        cms_obj.year_of_publication = year
        cms_obj.date_of_publication = monthdate
        cms_obj.access_date = today
        cms_obj.publisher_name = article['AuthorSite']

        cms = '* [{}. {}. "{}" Site, {}. Accessed {}.]({})'.format(
                article['AuthorSite'], year, article['Title'], monthdate, today, article['Url'])
        return (cms, cms_obj)


    #--------------------------------------------------------------------
    def scrape(self, article, withText=False, toPrint=False):
        """Scrape a single article."""
        self.log("Info: Scraping " + article['link'] + ' ...')
        item = self.__scrape_article(article, withText)
        item['Url'] = article['link']
        if item:
            item['CMS'], item['CMS-ADF'] = self.make_cms(item)

            self.news_items.append(item)
            if toPrint:
                self.print_article('item', item, withText)
        return item
    
        
    #--------------------------------------------------------------------
    def clean_url(self, url):
        """Clean URLs."""
        url = re.sub(r'&amp;','&',url) # when taken from DB, &amp; is present
        url = re.sub(r'.*&url=(http.*?)&ct=ga&.*','\\1',url) # coming Google alerts feed, use the target URL only
        return url
    
    
    #--------------------------------------------------------------------
    def __scrape_article(self, article, withText=True):
        """Scrape a single article passed in as a dictionary."""
        soup = BeautifulSoup(article['fullcontent'], 'lxml')
        soup = BeautifulSoup(soup.prettify('utf-8'), 'lxml') # some inputs are so messy that they affect the output
            
        # Get as much info as possible from metadata
        news_item = self.__get_metadata(soup)

        # Get the main text if necessary
        item = None
        if withText:
            news_item['FullText'] = self.__extract_text(soup)
            if news_item['FullText']:
                item = copy.deepcopy(news_item)
                self.news_items.append(item)
            #else: Skip this article if full text is not available
        else:
            item = copy.deepcopy(news_item)
            self.news_items.append(item)
        
        return item


    #--------------------------------------------------------------------
    def __get_metadata(self, soup):
        news_item = self.__make_item()
        self.__controller(news_item, soup)
        return news_item


    #--------------------------------------------------------------------
    def __make_item(self):
        return dict((x, None) for x in self.fields)
    
    
    #--------------------------------------------------------------------
    def __controller(self, news_item, soup):
        """Pass the new item to each html parser function."""
        self.page_count += 1
        html_parse_functions = [self.__parsley_meta,
                                self.__microdata,
                                self.__opengraph,
                                self.__site_specific]

        for parse_function in html_parse_functions:
            parse_function(news_item, soup)


    #--------------------------------------------------------------------
    def __parsley_meta(self, news_item, soup):
        """Scrape the html document for parsley tags."""
        parsely_keys = {'link': 'Url',
                        'title': 'Title',
                        'pub_date': 'SrcDate',
                        'author': 'AuthorSite',
                        'image_url': 'Image',
                        'summary': 'FirstText'}
        # extract content of the parsely tag and convert to dict
        if soup.find(attrs={"name": "parsely-page"}):
            # no. of pages that use parsely
            self.parsely_count += 1
            # search for parsely meta
            meta_content = soup.find(attrs={"name": "parsely-page"})['content']
            try:
                # convert the parsley dict to a python dict
                content_dict = eval(meta_content)
            except Exception:
                # TODO Find actual causes of parsely eval failure
                self.log("Warn: Unable to run eval() on parsely meta content. Skipping ...")
                return
        else:
            content_dict = {}
        
        # write contents or parsely tags to news_itmes
        for key in parsely_keys:
            if key in content_dict:
                if key == 'link' or key == 'image_url':
                    # special case to remove escape chars from url
                    news_item[parsely_keys[key]] = content_dict[key].decode('utf-8').replace('\/','/')
                elif key == 'pub_date':
                    news_item[parsely_keys[key]] = self.__date(struct = iso8601.parse_date(content_dict[key].decode('utf-8')).timetuple())
                elif key == 'summary' or key == 'author':
                    # remove all the white spaces
                    summary = content_dict[key].decode('utf-8')
                    summary = " ".join(summary.split())
                    news_item[parsely_keys[key]] = summary
                else:
                    news_item[parsely_keys[key]] = content_dict[key].decode('utf-8')

    
    #--------------------------------------------------------------------
    def __contains_microdata(self, tag):
        """Helper method for finding opengraph meta data."""
        return tag.has_attr('itemprop')


    #--------------------------------------------------------------------
    def __get_microdata_value(self, field):
        """Helper method for __microdata for field retrieval."""
        # extract specific fields
        if field.has_attr('href'):
            return field['href']
        elif field.has_attr('src'):
            return field['src']
        elif field.has_attr('content'):
            # TODO remove control characters from any strings
            text = field['content'].split()
            return ' '.join(text)
        else:
            text = field.get_text().split()
            return ' '.join(text)
            
            
    #--------------------------------------------------------------------
    def __microdata(self, news_item, soup):
        """Scrapes the html document for microdata based on http://schema.org/CreativeWork"""
        microdata_keys = {'url': 'Url',
                      'headline': 'Title',
                      'datePublished': 'SrcDate',
                      'author': 'AuthorSite',
                      'image': 'Image',
                      'description': 'FirstText'}
        
        # check for existance of microdata and add to count if present
        # bs4 allows a function to be passed in this manner to find_all()
        self.microdata = soup.find_all(self.__contains_microdata)
        
        if self.microdata:
            self.microdata_count += 1
            
        for key in microdata_keys:
            # only fill values that are missing i.e. set to None
            if news_item[microdata_keys[key]] == None:
                #retrieve each of the fields if the exist
                if key == 'url':
                    url_exists = soup.find_all(itemprop=key)
                    if url_exists:
                        # some pages contain more than one itemprop='url'
                        # this section is arbitrary
                        if len(url_exists) > 1:
                            # TODO refactor these lines into __get_microdata_value, low priority
                            news_item[microdata_keys[key]] = self.__get_microdata_value(url_exists[1])
                        else:
                            news_item[microdata_keys[key]] = self.__get_microdata_value(url_exists[0])
                                
                elif key == 'headline':
                    headline_exists = soup.find(itemprop=key)
                    if headline_exists:
                        news_item[microdata_keys[key]] = self.__get_microdata_value(headline_exists)
                        
                elif key == 'datePublished':
                    datepublished_exists = soup.find(itemprop=key)
                    if datepublished_exists:
                        news_item[microdata_keys[key]] = self.__get_microdata_value(datepublished_exists)
                        
                elif key == 'author':
                    # some pages have more than one author name
                    # TODO strip out any control character from the output (\n\t )
                    authors_exist = soup.find_all(itemprop=key)
                    if authors_exist:
                        if authors_exist[0].has_attr('content'):
                            #names = [" ".join(name['content'].encode('utf-8').split()) for name in authors_exist]
                            #news_item[microdata_keys[key]] =  ", ".join(names)
                            news_item[microdata_keys[key]] =  authors_exist[0]['content']
                        else:
                            names = [" ".join(name.text.encode('utf-8').split()) for name in authors_exist]
                            news_item[microdata_keys[key]] =  ", ".join(names)
                            
                elif key == 'image':
                    image_exists = soup.find(itemprop=key)
                    if image_exists:
                        news_item[microdata_keys[key]] = self.__get_microdata_value(image_exists)
                        
                elif key == 'description':
                    description = soup.find(itemprop=key)
                    #print description.get_text()
                    if description:
                        news_item[microdata_keys[key]] = self.__get_microdata_value(description)

    
    #--------------------------------------------------------------------
    def __contains_opengraph(self, tag):
        """Helper method for finding opengraph meta data."""
        return tag.has_attr('property')
    
    
    #--------------------------------------------------------------------
    def __opengraph(self, news_item, soup):
        """Extract meta tags for the Open Graph Protocol."""
        # TODO Sharing AuthorSite for two different fields causes complications
        opengraph_keys = {'og:url': 'Url',
                      'og:title': 'Title',
                      'article:published_time': 'SrcDate',
                      'og:author': 'AuthorSite',
                      'article:author': 'AuthorSite',
                      'og:site_name': 'AuthorSite',
                      'og:image': 'Image',
                      'og:description': 'FirstText'}

        self.opengraph = soup.find_all(self.__contains_opengraph)
        if self.opengraph:
            self.opengraph_count += 1
            
        for key in opengraph_keys:
            # only fill values that are missing i.e. set to None
            if news_item[opengraph_keys[key]] == None:
                opengraphdata = soup.find(property=key)
                if opengraphdata and opengraphdata.has_attr('content'):
                    if key == 'article:published_time':
                        try:
                            og_date = iso8601.parse_date(opengraphdata['content'])
                            news_item[opengraph_keys[key]] = self.__date(og_date.timetuple())
                        except iso8601.iso8601.ParseError as e:
                            self.log("Warn: Parse error for date field: " + str(e))
                            news_item[opengraph_keys[key]] = ''
                    else:
                        # reduce mutiple white spaces to a single white space
                        news_item[opengraph_keys[key]] = " ".join(opengraphdata['content'].split())


    #--------------------------------------------------------------------    
    def __site_specific(self, news_item, soup):
        """Scrape any remaining data not found in meta data."""
        domain = urlsplit(news_item['Url']).netloc
        
        # Processing for images
        if not news_item['Image'] and domain in self.sitemap and 'Image' in self.sitemap[domain]:
            attr, value, img_attr = self.sitemap[domain]['Image']
            image_section = soup.find(**{attr:value})
            if image_section and image_section.find_all('img', limit=1):
                if re.search(r'^https?://',image_section.img[img_attr]):
                    news_item['Image'] = image_section.img[img_attr]
                else: # convert to absolute URL
                    news_item['Image'] = 'http://' + "/".join([domain, image_section.img[img_attr]])
            else:
                self.log('Warn: Unable to find an image')
        
        # Other processing
        if domain == 'www.powersystemsdesign.com':
            # extract date
            date_section = soup.find(class_ = 'article-date')
            if date_section:
                # the dates are prefixed with 'Date: ', remove this
                date = date_section.text.split()
                date = "".join(date).split(':')[1]
                # convert date into correct format
                news_item['SrcDate'] = self.__date(time.strptime(str(date), "%m/%d/%Y"))
            # extract title
            title_section = soup.find(class_ = 'page-title')
            if title_section:
                news_item['Title'] = ''.join(title_section.text.strip())
        
        # site specific extraction of correct author string, this also fixes case of corrupted Author strings
        if domain in self.sitemap and 'Author' in self.sitemap[domain]:
            try:
                attr, value, extraction = self.sitemap[domain]['Author']
                news_item['AuthorSite'] = eval(extraction)
            except:
                self.log('Warn: Unable to find an Author for %s' % domain)


    #--------------------------------------------------------------------
    def __extract_text(self, soup):
        if not soup.body:
            self.log('Warn: HTML body does not exist. Please analyze URL content.')
            return
        
        for tag in ['script', 'style', 'br', 'iframe', 'img', 'embed']:
            self.__delete_tags(soup, tag)
        
        for tag in soup.body.descendants:
            if tag.name:                
                # Clear the inner content of unlikely tags
                for attr in ['class', 'id']:
                    if (attr in tag.attrs
                        and not re.search(HtmlScraper.tagCategories['positive'], str(tag.attrs[attr]), flags=re.I)
                        and re.search(HtmlScraper.tagCategories['unlikely'], str(tag.attrs[attr]), flags=re.I)):
                        #print "CLEARING:", tag.name, tag.encode('utf-8')
                        tag.clear()
                if ('style' in tag.attrs
                    and re.search(r'display\s*:\s*none',str(tag.attrs['style']), flags=re.I)):
                    # TODO Removing display:none won't work if JS shows such content after page loading
                    # TODO Review and retest: this is stripping out relevant content: eg. www.powersystemsdesign.com
                    #print "CLEARING:", tag.name, tag.encode('utf-8')
                    tag.clear()

        for tag in ['i', 'em', 'b', 'strong', 'blockquote']:
            self.__unwrap_tags(soup, tag)

        # If description exists in metadata, use that to resolve ambiguity
        desc = self.__process_metadata(soup)
        descTag = None

        longestTags = []
        for tag in soup.body.descendants:
            if not tag.name:
                if desc and not descTag and desc in tag.string:
                    descTag = tag
                    #print "Desc tag: [%s, %d] %s" % (descTag.parent.name, len(descTag.encode('utf-8')), descTag.parent.encode('utf-8')[:32])

                if (type(tag).__name__ != 'Comment'
                    and (not longestTags or len(longestTags[-1].string) < len(tag.string))):
                    #print "INNER:", tag.name, tag.encode('utf-8')
                    longestTags.append(tag)

        # Process all long tags and extract content from their sections/siblings
        allContent = []
        for longTag in reversed(longestTags):
            if not descTag or len(descTag.string)<len(longTag.string):
                if allContent and self.__clean_text(longTag.encode('utf-8')) in allContent[-1][2]:
                    #print "CONTINUING..."
                    continue
                contentTag = longTag.parent
            else:
                contentTag = descTag.parent
                
            if (not contentTag
                or not contentTag.parent
                or contentTag.name=='body'): break
            
            #print "Content tag: [%s, %d] %s" % (contentTag.name, len(contentTag.encode('utf-8')), contentTag.encode('utf-8')[:32])
            content = []
            textContent = []        
            for tag in contentTag.parent.children:
                linkWordDensity, linkDensity = self.__link_density(tag)
                #print "Tag Density:", tag.name, str(linkWordDensity), str(linkDensity), tag.encode('utf-8')[:40]
                if linkWordDensity<0.6 or linkDensity<0.6:
                    if tag.name==contentTag.name or re.search(r'(ul|ol)',str(tag.name)):
                        content.append(tag.encode('utf-8'))
                        textContent.append(tag.get_text().encode('utf-8'))
                        tag.clear()
            if content:
                linkWordDensity, linkDensity = self.__link_density(" ".join(content))
                #print "Full Density:", str(linkWordDensity), str(linkDensity), self.__clean_text(" ".join(textContent))[:100]
                if linkWordDensity<0.3 or linkDensity<0.3:
                    contentStr = self.__clean_text(" ".join(textContent))
                    wordCount = self.__word_count(contentStr)
                    paraCount = len(textContent)
                    #print "Counts add:", wordCount, paraCount, contentStr[:120]
                    allContent.append((wordCount, paraCount, contentStr))

        # There is absolutely no suitable content
        if not allContent:
            self.log('Info: No suitable content found.')
            return None
            
        # Select content giving preference to section with most words, then most paras
        allContent.sort(key=lambda i: (i[0], i[1]), reverse=True)
        foundContent = -1
        for i, content in enumerate(allContent):
            #print "Counts get:", content[0], content[1], content[2][:120]
            if content[0]>150 and content[1]>2:
                foundContent = i
                break
        
        # As last resort, ignore paragraph count
        if foundContent==-1 and allContent[0][0]>150:
            foundContent = 0

        if foundContent!=-1:
            contentStr = self.__trim(allContent[foundContent][2])
            return contentStr
        else:
            countStr = io.StringIO()
            for content in allContent:
                countStr.write('(%d, %d) ' % (content[0], content[1]))
            self.log('Info: No suitable content found. [Word count, Para count]: %s' % countStr.getvalue())
            countStr.close()
            return None

            
    #--------------------------------------------------------------------
    def __urlEncodeNonAscii(self, nonAscii):
        return re.sub('[\x80-\xFF]', lambda a: '%%%02X' % ord(a.group(0)), nonAscii)


    #--------------------------------------------------------------------
    def __iriToUri(self, iri):
        parts= urlparse(iri)
        return urlunparse(
            part.encode('idna') if i==1 else self.__urlEncodeNonAscii(part.encode('utf-8'))
            for i, part in enumerate(parts)
        )
        return urlunparse(parts)

    
    #--------------------------------------------------------------------
    def __article_date(self, rss_item, set_default=False):
        """Get the publication date of an article from its RSS entry."""
        pub_date = None
        if 'published_parsed' in rss_item and rss_item['published_parsed']:
            pub_date = rss_item['published_parsed']
        elif 'published' in rss_item and rss_item['published']:
            pub_date = rss_item['published']

            # TODO Perhaps could be simplified by using iso8601
            m = re.search(r'.*?(\d{1,2})\D(\d{1,2})\D(\d{4}).*?',pub_date)
            n = re.search(r'.*?(\d{4})\D(\d{1,2})\D(\d{1,2}).*?',pub_date)

            if m:
                pub_date = '%s-%s-%s' % (m.group(3),m.group(2),m.group(1))
            elif n:
                pub_date = '%s-%s-%s' % (n.group(1),n.group(2),n.group(3))

            if re.search(r'^\d+$',pub_date):
                pub_date = time.localtime(int(pub_date))
            elif re.search(r'^\d{4}-\d{1,2}-\d{1,2}$',pub_date):
                try:
                    pub_date = time.strptime(pub_date, '%Y-%m-%d')
                except ValueError:
                    pub_date = time.strptime(pub_date, '%Y-%d-%m')

        if set_default and not pub_date:
            pub_date = time.localtime()
            
        return pub_date


    #--------------------------------------------------------------------
    def __date(self, struct):
        """Format date in the form Month DD, YYYY. Example: January 24, 2014"""
        return time.strftime('%B %d, %Y', struct)


    #--------------------------------------------------------------------
    def __remove_html_tags(self, data):
        """Remove html tags."""
        p = re.compile(r'<[^<]*?/?>')
        return p.sub('', data)


    #--------------------------------------------------------------------
    def __trim(self, instr):
        instr = re.sub(r'^\s*[A-Z][A-Z]+\s*,?\s*\w*\s*:', '', instr)
        return instr
        
        
    #--------------------------------------------------------------------
    def __word_count(self, instr):
        words = re.split(r'[\s,;:.!]', instr)
        return len(words)
        
        
    #--------------------------------------------------------------------
    def __process_metadata(self, soup):
        desc = ''
        for tag in soup.find_all('meta'):
            # If description exists in metadata, use that to identify start of content
            if (('content' in tag.attrs and 'name' in tag.attrs and tag.attrs['name']=='description')
                or ('content' in tag.attrs and 'property' in tag.attrs and tag.attrs['property']=='og:description')):
                desc = str(tag.attrs['content'])

        return desc
    
    
    #--------------------------------------------------------------------
    def __clean_text(self, txt):
        txt = txt.strip()
        txt = re.sub(r'\s+',' ',txt)
        return txt
        
        
    #--------------------------------------------------------------------
    def __link_density(self, tag):
        """Find the link density given a tag or a string."""
        if type(tag).__name__=='str':
            tag = BeautifulSoup(tag, 'lxml')
            
        if not tag.name:
            return 0, 0
        
        textLen = len(tag.encode('utf-8'))
        if textLen==0:
            return 0, 0
        
        wordCount = len(tag.encode('utf-8').split())
        anchors = tag.find_all('a')
        anchorLen = 0
        anchorWordCount = 0
        for anchor in anchors:
            anchorWordCount += len(anchor.encode('utf-8').split())
            anchorLen += len(anchor.encode('utf-8'))

        return float(anchorWordCount)/wordCount, float(anchorLen)/textLen


    #--------------------------------------------------------------------
    def __delete_tags(self, soup, name):
        """Delete the tag completely from the parse tree."""
        for t in soup.find_all(name):
            if t.string: t.decompose()

        
    #--------------------------------------------------------------------
    def __clear_tags(self, soup, name):
        """Clear content of a tag."""
        for t in soup.find_all(name):
            if t.string: t.clear('')

        
    #--------------------------------------------------------------------
    def __unwrap_tags(self, soup, name):
        """Remove tag markup and preserve only inner text."""
        for t in soup.find_all(name):
            t.unwrap()
