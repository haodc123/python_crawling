from html.parser import HTMLParser
from urllib.parse import urljoin           # for join two urls
from urllib.request import urlopen         # for GET request
from helper import clean, checkIsExceptDomain, containStatic, isNoun, getDomain, sameDomain
from bs4 import BeautifulSoup, NavigableString, Tag
import gzip
import urllib.request
NUM_LINK_EACH_PAGE = 10

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

    def run(self, link, whatcrawling_mode, link_mode):
        self.whatcrawling_mode = whatcrawling_mode    # define craw link or craw content,...
        self.link = link                              # save root path
        self.arr_links = []                           # return crawling link list
        self.content = ""                             # return content of page
        self.title = ""   
        self.current_tag = ""
        self.link_mode = link_mode
        self.domain = getDomain(link)                 # get and save domain
        self.num_link = 0
        self.arr_crawled = []
        
        try:
            response = urlopen(link)                # request and get response
            html = response.read().decode("utf-8")  # read and encode response; NOTE: decode is necessary for unicode
            response.close()
            if whatcrawling_mode == "link":
                self.feed(html)                     # parse the html and parse link
                return self.arr_links
        except KeyboardInterrupt:                   # deal with Ctrl-C
            exit()
        except:
            try:
                print("1."+link)
                req = urllib.request.Request(url = link)
                req.add_header('Accept-encoding', 'gzip')
                res = urllib.request.urlopen(req)
                res.info().get('Content-Encoding')
                gzip_data = gzip.GzipFile(fileobj=res)
                html = gzip_data.read().decode('utf-8')
                gzip_data.close()
                if whatcrawling_mode == "link":
                    self.feed(html)                     # parse the html and parse link
                    return self.arr_links
            except:
                try:
                    req = urllib.request.Request(link, headers={'User-Agent' : "Magic Browser"})
                    f = urllib.request.urlopen(req)
                    html = f.read().decode("UTF-8") 
                    f.close()
                    print("2."+link)
                    if whatcrawling_mode == "link":
                        self.feed(html)                     # parse the html and parse link
                        return self.arr_links
                except:
                    print(link)
                    self.content = None
                    print("Unexpected failure happens and the spider escapes.")
                    return None     


class MySpider(object):
    def __init__(self):
        self.parser = MyHTMLParser()
    
    # craw to get link. Input:link, Output:link
    def crawLink(self, link, mode, outputFile, gd):
        target_link = clean(link)        
        if mode == "accident":
            link_mode = "search_result"       
        elif mode == "ordinary":
            link_mode = "same_side"
            
        print("Craw link for: "+target_link)
        
        gd.write("**** Craw link for: "+target_link+"\n")

        links = self.parser.run(target_link, "link", link_mode)    
        #print("craw_link "+''.join(links))
        if links is not None:
            for l in links:
                if l is not None: gd.write(" + "+l+"\n")

