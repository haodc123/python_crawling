from html.parser import HTMLParser
from urllib.parse import urljoin           # for join two urls
from urllib.request import urlopen         # for GET request
from helper import clean, checkIsExceptDomain, containStatic

FILE_500_PAGE_ACCIDENTS = "traffic_accidents\\500_page_accidents.txt"
FILE_500_PAGE_ACCIDENTS_CONTENT = "traffic_accidents\\500_page_accidents_content.txt"

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        
        # Overrid of the default function to handle <a> and ??? tags
        if self.whatcrawling_mode == "link":        # only run when crawling link mode
            for key, val in attrs:
                if key == "href":
                    if containStatic(val):             
                        pass
                    elif tag == "a":                      # handle links
                        link = urljoin(self.link, val)    # append relative path to the root path
                        link = clean(link)                # clean up link
                        if not checkIsExceptDomain(link):
                            self.links.append(link)       # append link to the return list
                    else:
                        pass

    '''
    TODO: Fix meeeee:
    def handle_data(self, data):    # print content of page
        if self.whatcrawling_mode == "content":
            with open(FILE_500_PAGE_ACCIDENTS_CONTENT, "a", encoding="utf-8") as gd:
                gd.write(data)
    '''
        
    def run(self, link, whatcrawling_mode):
        '''
        Run the parser and return links in this page
        '''
        self.whatcrawling_mode = whatcrawling_mode    # define craw link or craw content,...
        self.link = link                              # save root path
        self.links = []                               # return crawling link list

        try:
            response = urlopen(link)                # request and get response
            html = response.read().decode("utf-8")  # read and encode response; NOTE: decode is necessary for unicode
            self.feed(html)                         # parse the html and parse link
        except KeyboardInterrupt:                   # deal with Ctrl-C
            exit()
        except:
            print("Unexpected failure happens and the spider escapes.")

        return self.links

class MySpider(object):
    def __init__(self):
        self.crawled = []              # list for already crawled links
        self.parser = MyHTMLParser()
    '''
    craw to get link. Input:link, Output:link
    '''
    def craw_link(self, link):
        target_link = clean(link)

        print("Craw keyword link for: "+target_link)
        print("1.1.C. Get top 10 URLs each....")
        with open(FILE_500_PAGE_ACCIDENTS, "a", encoding="utf-8") as gd:
            gd.write("**** Craw keyword link for: "+target_link+"\n")

        links = self.parser.run(link, "link")
        
        for l in links:
            if l not in self.crawled:
                with open(FILE_500_PAGE_ACCIDENTS, "a", encoding="utf-8") as gd:
                    gd.write(" + "+l+"\n")
            self.crawled.append(l)
        