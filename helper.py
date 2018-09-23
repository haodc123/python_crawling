from urllib.parse import urlparse   # for domain extraction
import re                       # for regular expression
from urllib.parse import quote
import string
import os
import glob

SEARCH_ENGINE = "https://bing.com/search?q="
EXCEPT_DOMAIN = ["bing.com", "javascript:void(0)", "microsoft.com"]

def clean(url):
    '''
    Clean up url by
        - always start with "http://" or "https://"
        - remove element jumping
        - remove last '/'
    @input:
        url     :   the url to be processed
    @output:
        url     :   the clean url
    '''
    # Deal with "http(s)://"
    if url[0:4] != "http":
        url = "http://" + url

    # Deal with "#"
    idx = url.find('#')
    if idx != -1:
        url = url[:idx]

    # Deal with last "/"
    l = len(url)
    if url[l - 1] == '/':
        url = url[:l - 1]

    return url


def getDomain(url):
    '''
    Get the domain of a given url
    @input:
        url     :   the url to be processed
    @output:
        domain  :   the domain of the url
    '''
    parsed_url = urlparse(url)
    return "{url.netloc}".format(url=parsed_url)

def urlToFileName(url):
    if "https" in url:
        return url[8:].split("?")[0].translate({ord(c): "_" for c in "!@#$%^&*()[]{};:,./<>?\|`"})
    elif "http" in url:
        return url[7:].split("?")[0].translate({ord(c): "_" for c in "!@#$%^&*()[]{};:,./<>?\|`"})

def sameDomain(url, domain):
    '''
    Check if the given url is valid (e.g. within in "gocardless.com" domain)
    @input:
        url     :   the url to be checked
    @output:
        valid?  :   if the url is valid
    '''
    if re.match(r'^https?://([\w-]*\.)?' + domain + r'.*$', url, re.M|re.I):
        return True
    else:
        return False

def checkIsExceptDomain(link):
    '''
    Check if the given link is in except domain or not
    @input:
        link     :   the link to be checked
    @output:
        valid?  :   if the link is in except domain or not
    '''
    is_except_domain = False
    for domain in EXCEPT_DOMAIN:
        #if re.match(r'^https?://([\w-]*\.)?' + domain + r'.*$', link, re.M|re.I):
        if domain in link:
            is_except_domain = True
    return is_except_domain


def containStatic(val):
    '''
    Check if a given val (relative path or url) contains static files
    @input:
        val         :   relative path or url
    @output:
        contain?    :   if the val contains a static file
    '''
    if re.match(r'^.*\.(jpg|jpeg|gif|png|css|js|ico|xml|rss|txt).*$', val, re.M|re.I):
        return True
    else:
        return False


def makeLinkFromKeyword(kw):
    return SEARCH_ENGINE+quote(kw)

def isNoun(w):
    isNoun = True
    if len(w) == 0 or len(w) == 1:
        isNoun = False
    if "www" in w or "http" in w:
        isNoun = False
    if any(char.isdigit() for char in w):
        isNoun = False
    invalidChars = set(string.punctuation)
    if any(char in invalidChars for char in w):
        isNoun = False
    return isNoun

def getAllFileInPath(ext, path):
    os.chdir(path)
    result = [i for i in glob.glob('*.{}'.format(ext))]
    return result

def goToPath(path):
    os.chdir(path)

def getCurrentPath():
    return str(os.getcwd())

def isFileExist(filePath):
    return os.path.isfile(filePath)