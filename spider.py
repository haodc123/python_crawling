from html.parser import HTMLParser
from urllib.parse import urljoin           # for join two urls
from urllib.request import urlopen         # for GET request
from helper import clean, checkIsExceptDomain, containStatic, isNoun, getDomain, sameDomain
from underthesea import pos_tag
from bs4 import BeautifulSoup, NavigableString, Tag

FILE_50_WORD_ACCIDENTS = "traffic_accidents\\50_accidents_words.txt"
FILE_500_PAGE_ACCIDENTS = "traffic_accidents\\500_page_accidents.txt"
FILE_ALL_ACCIDENTS_NOUNS = "traffic_accidents\\all_accident_nouns.txt"
FILE_3000_ACCIDENTS_NOUNS = "traffic_accidents\\3000_accident_nouns.txt"

FILE_50_ALEXA_ORDINARY_LINK = "ordinary_contents\\50_alexa_ordinary.txt"
FILE_500_PAGE_ORDINARY = "ordinary_contents\\500_page_ordinary.txt"
FILE_ALL_ORDINARY_NOUNS = "ordinary_contents\\all_ordinary_nouns.txt"
FILE_3000_ORDINARY_NOUNS = "ordinary_contents\\3000_ordinary_nouns.txt"

NUMBER_NOUN_FILTERED = 3000
NUMBER_LINK_EACH_PAIR = 500
NUM_LINK_EACH_PAGE = 10
NOT_CONTENT_TAG = ["script", "style", "video"]

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):

        if self.whatcrawling_mode == "link":              # only run when mode: crawling link
            if self.num_link < NUM_LINK_EACH_PAGE:
                # For craw link handle <a> and ??? tags
                for key, val in attrs:
                    if key == "href":
                        if containStatic(val):
                            pass
                        else:                                     # handle links
                            link = urljoin(self.link, val)        # append relative path to the root path
                            link = clean(link)                    # clean up link
                            
                            if (self.link_mode == "search_result" and not checkIsExceptDomain(link)) or (self.link_mode == "same_side" and sameDomain(link, self.domain)):
                                if link.lower() not in self.arr_crawled:
                                    self.arr_links.append(link)       # append link to the return list
                                    self.num_link += 1
                                    self.arr_crawled.append(link.lower())
                

        '''
        elif self.whatcrawling_mode == "content":         # only run when mode: crawling content
            # For check tag to craw right content
            self.current_tag = tag
            self.not_content_link = False
            if tag == "a":
                for key, val in attrs:
                    if key == "title" and val != "":      # Not content link (Menu, advertisement,...)
                        self.not_content_link = True  
            if tag == "footer":
                self.inside_footer = True
        '''
    '''
    def handle_data(self, data):                          # print content of page
        if self.whatcrawling_mode == "content":           # only run when mode: crawling content
            if data.strip() != "" and self.current_tag not in NOT_CONTENT_TAG and self.not_content_link == False and self.inside_footer == False:
                self.content += " "+data
    '''

    def run(self, link, whatcrawling_mode, link_mode):
        self.whatcrawling_mode = whatcrawling_mode    # define craw link or craw content,...
        self.link = link                              # save root path
        self.arr_links = []                           # return crawling link list
        self.content = ""                             # return content of page
        self.current_tag = ""
        self.link_mode = link_mode
        self.domain = getDomain(link)                 # get and save domain
        self.num_link = 0
        self.arr_crawled = []
        #self.not_content_link = False
        #self.inside_footer = False
        
        try:
            response = urlopen(link)                # request and get response
            html = response.read().decode("utf-8")  # read and encode response; NOTE: decode is necessary for unicode
            if whatcrawling_mode == "link":
                self.feed(html)                     # parse the html and parse link
                return self.arr_links
            elif whatcrawling_mode == "content":
                self.content = ParseContent.htmlToText(str(html))
                return self.content
        except KeyboardInterrupt:                   # deal with Ctrl-C
            exit()
        except:
            self.content = ""            
            print("Unexpected failure happens and the spider escapes.")
            return self.content


class MySpider(object):
    def __init__(self):
        self.parser = MyHTMLParser()
    
    # craw to get link. Input:link, Output:link
    def craw_link(self, link, mode):
        if mode == "accident":
            link_mode = "search_result"
            file_500page = FILE_500_PAGE_ACCIDENTS
            print("Craw link for: "+target_link)
            print("1.1.C. Get 10 URLs each...")
        elif mode == "ordinary":
            link_mode = "same_side"
            file_500page = FILE_500_PAGE_ORDINARY
            print("Craw link for: "+target_link)
            print("1.2.C. Get 10 URLs each...")

        target_link = clean(link)

        with open(file_500page, "a", encoding="utf-8", errors='ignore') as gd:
            gd.write("**** Craw link for: "+target_link+"\n")

        links = self.parser.run(target_link, "link", link_mode)
        
        for l in links:
            with open(file_500page, "a", encoding="utf-8", errors='ignore') as gd:
                gd.write(" + "+l+"\n")

    
    def craw_content(self, link):
        target_link = clean(link)

        print("Craw content for: "+target_link)
        content = self.parser.run(target_link, "content", "")
        return content

    


class ParseContent():
    def htmlToText(html):
        soup = BeautifulSoup(html, 'html.parser')
        # Ignore anything in head
        body, text = soup.body, []
        print(text)
        for element in body.descendants:
            if type(element) == NavigableString:
                parent_tags = (t for t in element.parents if type(t) == Tag)
                hidden = False
                for parent_tag in parent_tags:
                    # Ignore any text inside a non-displayed tag
                    if (parent_tag.name in ('em', 'input', 'button', 'area', 'base', 'basefont', 'datalist', 'head', 'link',
                                            'meta', 'noembed', 'noframes', 'param', 'rp', 'script',
                                            'source', 'style', 'template', 'track', 'title', 'noscript', 
                                            'footer', 'a', 'select') or
                        parent_tag.has_attr('hidden') or
                        (parent_tag.name == 'input' and parent_tag.get('type') == 'hidden')):
                        hidden = True
                        break
                if hidden:
                    continue

                # remove any multiple and whitespace
                string = ' '.join(element.string.split())
                if string:
                    if element.parent.name == 'p':
                        # Add extra paragraph formatting newline
                        string = '\n' + string
                        #print(string)
                    text += [string]
        doc = ' '.join(text)
        return doc    
        