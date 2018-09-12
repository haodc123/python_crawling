from html.parser import HTMLParser
from urllib.parse import urljoin           # for join two urls
from urllib.request import urlopen         # for GET request
from helper import clean, checkIsExceptDomain, containStatic, isNoun
from underthesea import pos_tag
from bs4 import BeautifulSoup, NavigableString, Tag

FILE_500_PAGE_ACCIDENTS = "traffic_accidents\\500_page_accidents.txt"
FILE_ALL_ACCIDENTS_NOUNS = "traffic_accidents\\all_accident_nouns.txt"
FILE_3000_ACCIDENTS_NOUNS = "traffic_accidents\\3000_accident_nouns.txt"
NOT_CONTENT_TAG = ["script", "style", "video"]
NUMBER_NOUN_FILTERED = 3000

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):

        if self.whatcrawling_mode == "link":              # only run when mode: crawling link
            # For craw link handle <a> and ??? tags
            for key, val in attrs:
                if key == "href":
                    if containStatic(val):
                        pass
                    else:                                 # handle links
                        link = urljoin(self.link, val)    # append relative path to the root path
                        link = clean(link)                # clean up link
                        if not checkIsExceptDomain(link):
                            self.arr_links.append(link)       # append link to the return list
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

    def run(self, link, whatcrawling_mode):
        self.whatcrawling_mode = whatcrawling_mode    # define craw link or craw content,...
        self.link = link                              # save root path
        self.arr_links = []                           # return crawling link list
        self.content = ""                             # return content of page
        self.current_tag = ""
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
        self.arr_crawled = []              # list for already crawled links
        self.parser = MyHTMLParser()
    
    # craw to get link. Input:link, Output:link
    def craw_link(self, link):
        target_link = clean(link)

        print("Craw keyword link for: "+target_link)
        print("1.1.C. Get top 10 URLs each...")
        with open(FILE_500_PAGE_ACCIDENTS, "a", encoding="utf-8") as gd:
            gd.write("**** Craw keyword link for: "+target_link+"\n")

        links = self.parser.run(target_link, "link")
        
        for l in links:
            if l not in self.arr_crawled:
                with open(FILE_500_PAGE_ACCIDENTS, "a", encoding="utf-8") as gd:
                    gd.write(" + "+l+"\n")
            self.arr_crawled.append(l)
    
    def craw_content(self, link):
        target_link = clean(link)

        print("Craw content for: "+target_link)
        content = self.parser.run(target_link, "content")
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
        