# coding=utf8
'''
1. Gathering teacher data
    1.1. Get traffic accident contents
        A. List up 50 words which deeply relate to traffic accidents.
        B. Google 50 words separately.
        C. Get top 10 URLs each.
        D. Crawling 500 pages.
        E. Get all the texts in each page.
        F. Separate and extract all the noun words using the morphing analysis tool.
        G. Count all the noun words together and align  them desc and pick up 3000 words
    1.2. Get ordinary contents
        A. List up top 50 Vietnamese sites. using similarweb and/or Alexa . 
        B. Crawling 10 pages for each site.
        C. DO the same things from "E" of "Get traffic accident contents"
    . 
    1.3. Make teacher data
        A. Make two folders: traffic_accidents, ordinary_contents
        B. Make 1000 files (500 each folder corresponding 500 URLs)

        file name : URL
        file format :
        word1, word2, .................word3000, word3001, word3002,...............word6000
        count (word1), count(word2),.................................................................., word6000
        
        Each file: 
        - line 1: 3000 words releated traffic accident + 3000 words ordinary contents (all file same)
        - line 2: count each words in each URLs
        
2.Modeling
    A. Load 1000 files
    B. Model using randomforest
3.Verification
    A. Input URL
    B. Crawl it
    C. Separate and extract all the noun words using the morphing analysis tool
    D. Count all the noun words
    E. Make CSV file
    F. Verify
'''
import sys
from spider import MySpider, ParseHTMLManual
from helper import *
from modeling import MyModeling
from underthesea import pos_tag
import requests
from collections import Counter
import csv
import threading
import time
from queue import Queue
import re
import numpy as np

FILE_50_WORD_ACCIDENTS = "traffic_accidents\\50_accidents_words.txt"
FILE_500_PAGE_ACCIDENTS = "traffic_accidents\\500_page_accidents.txt"
FILE_ALL_ACCIDENTS_NOUNS = "traffic_accidents\\all_accident_nouns.txt"
FILE_3000_ACCIDENTS_NOUNS = "traffic_accidents\\3000_accident_nouns.txt"

FILE_50_ALEXA_ORDINARY_LINK = "ordinary_contents\\50_alexa_ordinary.txt"
FILE_500_PAGE_ORDINARY = "ordinary_contents\\500_page_ordinary.txt"
FILE_ALL_ORDINARY_NOUNS = "ordinary_contents\\all_ordinary_nouns.txt"
FILE_3000_ORDINARY_NOUNS = "ordinary_contents\\3000_ordinary_nouns.txt"

NUMBER_NOUN_FILTERED = 3000
NUMBER_LINK_EACH_PAIR = 530

NUM_WORKERS = 200 #threading
listAccidentURL = set()
listOrdinaryURL = set()
#listAccidentURL2 = set()
#listOrdinaryURL2 = set()
urls = Queue()
urls2 = Queue()
urls3 = Queue()
urlsO = Queue()
urlsO2 = Queue()
urlsO3 = Queue()

'''
Usage:
    type: python main.py --tra
    for 1.1. Get traffic accident contents
    type: python main.py --ord
    for 1.2. Get ordinary contents
'''
def main():
    arr_500_accident_link = []
    arr_500_ordinary_link = []
    args = sys.argv[1:]
    
    if len(args) == 1 and args[0] == "--link_tra":
        mode = "accident"
        getLink(mode, FILE_50_WORD_ACCIDENTS, FILE_500_PAGE_ACCIDENTS)
    elif len(args) == 1 and args[0] == "--content_tra":
        start = time.time()
        mode = "accident"
        getContent(mode, FILE_50_WORD_ACCIDENTS, FILE_500_PAGE_ACCIDENTS)                     
        print('1.1. Get traffic accident contents:', time.time() - start)
    elif len(args) == 1 and args[0] == "--tra":        # 1.1. Get traffic accident contents
        start = time.time()
        mode = "accident"
        getLink(mode, FILE_50_WORD_ACCIDENTS, FILE_500_PAGE_ACCIDENTS)
        getContent(mode, FILE_50_WORD_ACCIDENTS, FILE_500_PAGE_ACCIDENTS)                     
        print('1.1. Get traffic accident contents:', time.time() - start)
    
    elif len(args) == 1 and args[0] == "--link_ord":
        mode = "ordinary"
        getLink(mode, FILE_50_ALEXA_ORDINARY_LINK, FILE_500_PAGE_ORDINARY)
    elif len(args) == 1 and args[0] == "--content_ord":      # 1.2. Get ordinary contents
        start = time.time()
        mode = "ordinary"
        getContent(mode, FILE_50_ALEXA_ORDINARY_LINK, FILE_500_PAGE_ORDINARY)
        print('1.2. Get ordinary contents:', time.time() - start)
    elif len(args) == 1 and args[0] == "--ord":      # 1.2. Get ordinary contents
        start = time.time()
        mode = "ordinary"
        getLink(mode, FILE_50_ALEXA_ORDINARY_LINK, FILE_500_PAGE_ORDINARY)
        getContent(mode, FILE_50_ALEXA_ORDINARY_LINK, FILE_500_PAGE_ORDINARY)
        print('1.2. Get ordinary contents:', time.time() - start)
    
    elif len(args) == 1 and args[0] == "--file":     # 1.3. Make teacher data
        start = time.time() 
        addLinkToQueue(FILE_500_PAGE_ACCIDENTS, "accident")
        create1000File("accident", listAccidentURL)
        addLinkToQueue(FILE_500_PAGE_ORDINARY, "ordinary")           
        create1000File("ordinary", listOrdinaryURL)
        print('1.3. Make teacher data:', time.time() - start)
    elif len(args) == 1 and args[0] == "--mix":      # 1.1 + 1.2 + 1.3. Make teacher data
        start = time.time()
        getLink("accident", FILE_50_WORD_ACCIDENTS, FILE_500_PAGE_ACCIDENTS)
        getContent("accident", FILE_50_WORD_ACCIDENTS, FILE_500_PAGE_ACCIDENTS)
        getLink("ordinary", FILE_50_ALEXA_ORDINARY_LINK, FILE_500_PAGE_ORDINARY)
        getContent("ordinary", FILE_50_ALEXA_ORDINARY_LINK, FILE_500_PAGE_ORDINARY)
        create1000File("accident", listAccidentURL)
        create1000File("ordinary", listOrdinaryURL)
        print('1.1 + 1.2 + 1.3. Make teacher data:', time.time() - start)
    
    elif len(args) == 1 and args[0] == "--model":
        # 2. Modeling
        mmd = MyModeling("regressor")
        mmd.createModel()
        mmd.testModelRegressor()
    elif len(args) == 1 and args[0] == "--model2":
        # 2. Modeling
        mmd = MyModeling("classifier")
        mmd.createModel()
        mmd.testModelClassifier()
    elif len(args) == 2 and args[0] == "--model" and args[1] != "":
        # 2. Modeling + 3. Validation
        link = clean(args[1])
        createValidationData(link)
        mmd = MyModeling("regressor")
        mmd.validateModel(link)
    elif len(args) == 2 and args[0] == "--model2" and args[1] != "":
        # 2. Modeling + 3. Validation
        link = clean(args[1])
        createValidationData(link)
        mmd = MyModeling("classifier")
        mmd.validateModel(link)
    
    elif args[0] == "--test":
        test()
    else:
        print("Wrong syntax, please try again!")

# 1.1. Get traffic accident contents
def getContent(mode, wordFile, urlFile):
    if ("accident" == mode):
        file = FILE_ALL_ACCIDENTS_NOUNS
    else: 
        file = FILE_ALL_ORDINARY_NOUNS
    
    print("D. Crawling 500 pages from 500_page_accidents.txt....")
    
    addLinkToQueue(urlFile, mode)
    spider = MySpider()
    with open(file, "a", encoding="utf-8", errors='ignore') as gd:
        create_workersGetContent(mode, spider, gd)
        create_jobs(mode) 
        create_jobs2(mode) 
        create_jobs3(mode)
        gd.close()
    
    print("G. Count all the noun words together and align  them desc and pick up 3000 words...")
    countAndGetCommonNounFromFile(mode)
    
def getLink(mode, wordFile, urlFile):
    print("1.1.A. Read 50 VNese word related to traffic accidents from accidents.txt...")
    tra_words = [line.rstrip('\n') for line in open(wordFile, encoding="utf8")]
    tra_words = tra_words[1:]    # bypass first row
    
    print("B. Google 50 words seperate (using Bing replace)...")
    spider = MySpider()
    print("C. Get 10 URLs each...")
    if mode == "accident":
        file_500_links = FILE_500_PAGE_ACCIDENTS
    elif mode == "ordinary":
        file_500_links = FILE_500_PAGE_ORDINARY   
        
    with open(file_500_links, "a", encoding="utf-8", errors='ignore') as gd:
        for w in tra_words:
            if ("accident" == mode):
                link = makeLinkFromKeyword(w)
            elif ("ordinary" == mode):
                link = w   
            spider.craw_link(link, mode, file_500_links, gd)
        gd.close()

# Create count noun file for validation file
def createValidationData(link):
    spider = MySpider()
    mode = "validation"
    content = spider.crawContent(link)
    saveContentEachPage(content, link, mode)
    createFileCountNoun(mode, link, FILE_3000_ACCIDENTS_NOUNS, FILE_3000_ORDINARY_NOUNS)

def addLinkToQueue(urlFile, mode):
    tra_links = [line.rstrip('\n') for line in open(urlFile, encoding="utf8", errors='ignore')]
    for url in tra_links:        
        #if "**** Craw link for" in str(url):
        #    continue
        if url[:3] == " + ":
            if ("youtube" in str(url[3:])):            
                tmp = url[3:]
            else: 
                tmp = url[3:].split('?')[0]
            if (mode == "accident"): 
                listAccidentURL.add(tmp) 
            elif (mode == "ordinary"):
                listOrdinaryURL.add(tmp)
       
# 1.3. Make teacher data
def create1000File(mode, listURLs):
    print("1.3.B. Make 1000 files (500 each folder corresponding 500 URLs)...")   
    for url in listURLs:
        createFileCountNoun(mode, url, FILE_3000_ACCIDENTS_NOUNS, FILE_3000_ORDINARY_NOUNS)

def get500LinksFromFile(mode):
    if mode == "accident":
        file_500_links = FILE_500_PAGE_ACCIDENTS
    elif mode == "ordinary":
        file_500_links = FILE_500_PAGE_ORDINARY

    links_line = [line.rstrip('\n') for line in open(file_500_links, encoding="utf8")]
    arr_500links = []
    for l in links_line:
        if l[:3] == " + ":
            if len(arr_500links) >= NUMBER_LINK_EACH_PAIR:
                break
            arr_500links.append(l[3:])
    return arr_500links


def saveContentEachPage(content, url, mode):
    if content is not None and len(content.strip()) > 0:
        if mode == "accident":
            file_content_page = "traffic_accidents\\content_accidents_page_"+urlToFileName(url)+".txt"
            #print(urlToFileName(url))
            print("1.1.E. Get all the texts in each page...")
            print("1.1.F. Separate and extract all the noun words using the morphing analysis tool...")
        elif mode == "ordinary":
            file_content_page = "ordinary_contents\\content_ordinary_page_"+urlToFileName(url)+".txt"
            print("1.2.E. Get all the texts in each page...")
            print("1.2.F. Separate and extract all the noun words using the morphing analysis tool...")
        elif mode == "validation":
            file_content_page = "modeling\\validation\\content_"+urlToFileName(url)+".txt"
            print("3.B. Crawl it...")
        
        with open(file_content_page, "a", encoding="utf-8") as gd:
            print(urlToFileName(url)+" writting txt... ")
            #print(content)
            gd.write(content)
            gd.close()
            print(urlToFileName(url)+" write OK")
        
def getContentfromTxtfile(content, gd): 
    if (content is not None and len(content.strip()) > 0):
        tmp = extractNoun(str(content))
        if len(tmp) > 0:
            arr_nouns = ", ".join(tmp)
            print(arr_nouns)
            gd.write(arr_nouns.lower())
            gd.write("\n")
    
'''def getContentfromTxtfile(url, mode, gd):  
    if mode == "accident":
        # Read content file each page
        File = open("traffic_accidents\\content_accidents_page_"+urlToFileName(url)+".txt", encoding="utf-8", errors='ignore')
        content = File.read()
        File.close()
    elif mode == "ordinary":
        # Read content file each page
        File = open("ordinary_contents\\content_ordinary_page_"+urlToFileName(url)+".txt", encoding="utf-8", errors='ignore')
        content = File.read()
        File.close()  
    #print(content)
    arr_nouns = ", ".join(extractNoun(str(content)))
    print(arr_nouns)
    gd.write(arr_nouns+", ")
    gd.write("\n")
'''
def extractNoun(content):
    arr_nouns = []
    if (content is not None and len(content.strip()) > 0):
        for word,pos in pos_tag(content):
            if (pos == 'N' and isNoun(word)):
                arr_nouns.append(word)
    return arr_nouns

def createFileCountNoun(forwhich, url, filenameAccidentNoun, filenameOrdinaryNoun):
    # Read 3000 accident noun from file
    File = open(filenameAccidentNoun, encoding="utf-8", errors='ignore')
    accident_nouns = File.read()
    arr_accident_noun = re.split(', |\n',accident_nouns)
    #arr_accident_noun = accident_nouns.split(", ")
    File.close()
    # Read 3000 ordinary noun from file
    File = open(filenameOrdinaryNoun, encoding="utf-8", errors='ignore')
    ordinary_nouns = File.read()
    arr_ordinary_noun = re.split(', |\n',ordinary_nouns)
    #arr_ordinary_noun = ordinary_nouns.split(", ")
    File.close()
    
    fileName = urlToFileName(url)
    if forwhich == "accident":
        # Read content file each page
        File = open("traffic_accidents\\content_accidents_page_"+fileName+".txt", encoding="utf-8", errors='ignore')
        content = File.read()
        csv_file_name = open("traffic_accidents//training_data//"+fileName+".csv", 'w', encoding="utf-8", errors='ignore', newline='')
        File.close()
    elif forwhich == "ordinary":
        # Read content file each page
        File = open("ordinary_contents\\content_ordinary_page_"+fileName+".txt", encoding="utf-8", errors='ignore')
        content = File.read()
        csv_file_name = open("ordinary_contents//training_data//"+fileName+".csv", 'w', encoding="utf-8", errors='ignore', newline='')
        File.close()
    elif forwhich == "validation":
        # Read content file each page
        File = open("modeling\\validation\\content_"+fileName+".txt", encoding="utf-8", errors='ignore')
        content = File.read()
        csv_file_name = open("modeling\\validation\\"+fileName+".csv", 'w', encoding="utf-8", errors='ignore', newline='')
        File.close()

    # Count noun in content
    csv_data = [[], []]
    for noun in arr_accident_noun:
        if len(noun) > 0:
            count = str(content).count(noun)
            csv_data[0].append(noun)
            csv_data[1].append(count)
    for noun in arr_ordinary_noun:
        if len(noun) > 0:
            count = str(content).count(noun)
            csv_data[0].append(noun)
            csv_data[1].append(count)
    # write CSV file
    with csv_file_name:
        writer = csv.writer(csv_file_name)
        writer.writerows(csv_data)
        print(csv_data)
        csv_file_name.close()

def countAndGetCommonNounFromFile(mode):
    if mode == "accident":
        file_all_noun = FILE_ALL_ACCIDENTS_NOUNS
        file_3000_noun = FILE_3000_ACCIDENTS_NOUNS
    elif mode == "ordinary":
        file_all_noun = FILE_ALL_ORDINARY_NOUNS
        file_3000_noun = FILE_3000_ORDINARY_NOUNS

    File = open(file_all_noun, encoding="utf-8", errors='ignore')
    all_nouns = File.read()
    arr_all_noun = re.split(', |\n',all_nouns)
    arr_nouns = Counter(arr_all_noun).most_common(NUMBER_NOUN_FILTERED)
    File.close()  
    with open(file_3000_noun, "a", encoding="utf-8", errors='ignore') as gd:
        for word,num in arr_nouns:
            gd.write(word+", ")
        gd.close()

def do_addContent(mode, spider, gd): 
    while True:
        if ("accident" == mode):
            url = urls.get() 
            content = spider.crawContent(url)
            saveContentEachPage(content, url, mode)   
            getContentfromTxtfile(content, gd)
            urls.task_done()
        else:
            url1 = urlsO.get()  
            content = spider.crawContent(url1)
            saveContentEachPage(content, url1, mode)   
            getContentfromTxtfile(content, gd)        
            urlsO.task_done()
        
def do_addContent2(mode, spider, gd): 
    while True:
        if ("accident" == mode):
            url = urls2.get() 
            content = spider.crawContent(url)
            saveContentEachPage(content, url, mode)   
            getContentfromTxtfile(content, gd)
            urls2.task_done()
        else:
            url1 = urlsO2.get()  
            content = spider.crawContent(url1)
            saveContentEachPage(content, url1, mode)   
            getContentfromTxtfile(content, gd)        
            urlsO2.task_done()
    print("task done")
def do_addContent3(mode, spider, gd): 
    while True:
        if ("accident" == mode):
            url = urls3.get() 
            content = spider.crawContent(url)
            saveContentEachPage(content, url, mode)   
            getContentfromTxtfile(content, gd)
            urls3.task_done()
        else:
            url1 = urlsO3.get()  
            content = spider.crawContent(url1)
            saveContentEachPage(content, url1, mode)   
            getContentfromTxtfile(content, gd)        
            urlsO3.task_done()
    print("task done")
    
def create_workersGetContent(mode, spider, gd):
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=do_addContent, args = (mode, spider, gd))
        t2 = threading.Thread(target=do_addContent2, args = (mode, spider, gd))
        t3 = threading.Thread(target=do_addContent3, args = (mode, spider, gd))
        t.daemon = True
        t2.daemon = True
        t3.daemon = True
        t.start()
        t2.start()
        t3.start()
          
    
def create_jobs(mode):     
    if ("accident" == mode):
        for url in list(listAccidentURL)[:150]:
            urls.put(url)
        urls.join()
    else:
        for url in list(listOrdinaryURL)[:150]: 
            urlsO.put(url)
        urlsO.join()
def create_jobs2(mode):     
    if ("accident" == mode):
        for url in list(listAccidentURL)[150:300]:
            urls2.put(url)
        urls2.join()
    else:
        for url in list(listOrdinaryURL)[150:300]: 
            urlsO2.put(url)
        urlsO2.join()
def create_jobs3(mode):     
    if ("accident" == mode):
        for url in list(listAccidentURL)[300:]:
            urls3.put(url)
        urls3.join()
    else:
        for url in list(listOrdinaryURL)[300:]: 
            urlsO3.put(url)
        urlsO3.join()

def test():
    print("a")

        
if __name__ == "__main__":
    main()