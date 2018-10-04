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
from content import ContentHTML
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

NUMBER_NOUN_FILTERED = 1000

'''
Usage:
    2 step:
	A. Create data-output file:
    - Require file:
        traffic_accidents\\50_accidents_words.txt
        ordinary_contents\\50_alexa_ordinary.txt
    - Create data-output file:
		1. type: python main.py --tra
			for 1.1. Get traffic accident contents
		2. type: python main.py --ord
			for 1.2. Get ordinary contents
		3. type: python main.py --file
			for 1.3. Get 1000 file count Noun (csv)
    B. Validate link
        4. type: python main.py --model <link>
            for 3. Validation a link is releated to traffic accident or not (via regressor method)
        5. type: python main.py --model2 <link>
            for 3. Validation a link is releated to traffic accident or not (via classifier method)
'''
def main():
    arr_500_accident_link = []
    arr_500_ordinary_link = []
    args = sys.argv[1:]
    spider = MySpider()
    if len(args) == 1 and args[0] == "--link_tra":
        mode = "accident"
        getLink(mode, FILE_50_WORD_ACCIDENTS, FILE_500_PAGE_ACCIDENTS, spider)
    elif len(args) == 1 and args[0] == "--content_tra":     # 1.1. Get traffic accident contents
        start = time.time()
        mode = "accident"
        file = FILE_ALL_ACCIDENTS_NOUNS
        #call get content and count Noun,Verb
        ContentHTML.getContent(mode, spider, FILE_50_WORD_ACCIDENTS, FILE_500_PAGE_ACCIDENTS, file)
        #create file 3000 words
        countAndGetCommonNounFromFile(mode)
        print('1.1. Get traffic accident contents:', time.time() - start)       
    elif len(args) == 1 and args[0] == "--link_ord":
        mode = "ordinary"
        getLink(mode, FILE_50_ALEXA_ORDINARY_LINK, FILE_500_PAGE_ORDINARY, spider)
    elif len(args) == 1 and args[0] == "--content_ord":      # 1.2. Get ordinary contents
        start = time.time()
        mode = "ordinary"
        file = FILE_ALL_ORDINARY_NOUNS
        #call get content and count Noun,Verb
        ContentHTML.getContent(mode, spider, FILE_50_ALEXA_ORDINARY_LINK, FILE_500_PAGE_ORDINARY, file)
        #create file 3000 words
        countAndGetCommonNounFromFile(mode)
        print('1.2. Get ordinary contents:', time.time() - start)    
    elif len(args) == 1 and args[0] == "--file":     # 1.3. Make teacher data
        start = time.time() 
        ContentHTML.addLinkToQueue(FILE_500_PAGE_ACCIDENTS, "accident")
        ContentHTML.create1000File("accident", ContentHTML.listAccidentURL)
        ContentHTML.addLinkToQueue(FILE_500_PAGE_ORDINARY, "ordinary")           
        ContentHTML.create1000File("ordinary", ContentHTML.listOrdinaryURL)
        print('1.3. Make teacher data:', time.time() - start)    
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
    elif args[0] == "--manual":
        # For improve correctly, need to shorten FILE_3000_ACCIDENTS_NOUNS (get only traffic accident) by manual
        # Below steps are split and need to manual handle
        manual()
    else:
        print("Wrong syntax, please try again!")
    
# create file for 500links
def getLink(mode, wordFile, urlFile, spider):
    print("1.1.A. Read 50 VNese word related to traffic accidents from accidents.txt...")
    tra_words = [line.rstrip('\n') for line in open(wordFile, encoding="utf8")]
    tra_words = tra_words[1:]    # bypass first row
    
    print("B. Google 50 words seperate (using Bing replace)...")
    print("C. Get 10 URLs each...")
    if mode == "accident":
        file_500_links = FILE_500_PAGE_ACCIDENTS
    elif mode == "ordinary":
        file_500_links = FILE_500_PAGE_ORDINARY   
        
    with open(file_500_links, "a", encoding="utf-8-sig", errors='ignore') as gd:
        for w in tra_words:
            if ("accident" == mode):
                link = makeLinkFromKeyword(w)
            elif ("ordinary" == mode):
                link = w   
            spider.crawLink(link, mode, file_500_links, gd)
        gd.close()

# Create count noun file for validation file
def createValidationData(link):
    spider = MySpider()
    mode = "validation"
    content = spider.crawContent(link)
    ContentHTML.saveContentEachPage(content, link, mode)
    arr_accident_noun = ContentHTML.get3000wordsFromNounFile(FILE_3000_ACCIDENTS_NOUNS)
    arr_ordinary_noun = ContentHTML.get3000wordsFromNounFile(FILE_3000_ORDINARY_NOUNS)
    ContentHTML.createFileCountNoun(mode, link, arr_accident_noun, arr_ordinary_noun)
    
#sort word and write file
def countAndGetCommonNounFromFile(mode):
    if mode == "accident":
        file_all_noun = FILE_ALL_ACCIDENTS_NOUNS
        file_3000_noun = FILE_3000_ACCIDENTS_NOUNS
    elif mode == "ordinary":
        file_all_noun = FILE_ALL_ORDINARY_NOUNS
        file_3000_noun = FILE_3000_ORDINARY_NOUNS

    File = open(file_all_noun, encoding="utf-8-sig", errors='ignore')
    all_nouns = File.read()
    arr_all_noun = re.split(', |\n',all_nouns)
    arr_nouns = Counter(arr_all_noun).most_common(NUMBER_NOUN_FILTERED)
    print(len(arr_nouns))
    File.close()
    with open(file_3000_noun, "a", encoding="utf-8-sig", errors='ignore') as gd:
        for word, num in arr_nouns:
            gd.write(word+", ")
        gd.close()
    '''File = open(file_3000_noun, encoding="utf-8-sig", errors='ignore')
    accident_nouns = File.read().strip()
    arr_noun = re.split(', |\n',accident_nouns)[:-1]
    print(len(arr_noun))'''
    
def test():
    arr_accident_noun = ContentHTML.get3000wordsFromNounFile(FILE_3000_ACCIDENTS_NOUNS)
    arr_ordinary_noun = ContentHTML.get3000wordsFromNounFile(FILE_3000_ORDINARY_NOUNS)
    
    ContentHTML.createFileCountNoun("test", "", arr_accident_noun, arr_ordinary_noun)

def manual():
    manual_split()                  # step 1
    # manual filter accident noun   # step 2
    manual_join()                   # step 3
    manual_shortenOrdinaryFile()    # step 4
    # replace file from FILE_FILTERED_ACCIDENTS_NOUNS -> FILE_3000_ACCIDENTS_NOUNS, similar with ORDINARY   # step 5

def manual_split():
    arr_accident_noun = get3000wordsFromNounFile(FILE_3000_ACCIDENTS_NOUNS)
    #arr_accident_noun = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]
    file_accident_noun1 = "traffic_accidents\\manual_filter\\1.txt"
    file_accident_noun2 = "traffic_accidents\\manual_filter\\2.txt"
    file_accident_noun3 = "traffic_accidents\\manual_filter\\3.txt"
    file_accident_noun4 = "traffic_accidents\\manual_filter\\4.txt"
    step = int(len(arr_accident_noun)/4)
    with open(file_accident_noun1, "a", encoding="utf-8-sig", errors='ignore') as gd:
        for w in arr_accident_noun[:step]:
            gd.write(str(w)+", ")
        gd.close()
    with open(file_accident_noun2, "a", encoding="utf-8-sig", errors='ignore') as gd:
        for w in arr_accident_noun[step:step*2]:
            gd.write(str(w)+", ")
        gd.close()
    with open(file_accident_noun3, "a", encoding="utf-8-sig", errors='ignore') as gd:
        for w in arr_accident_noun[step*2:step*3]:
            gd.write(str(w)+", ")
        gd.close()
    with open(file_accident_noun4, "a", encoding="utf-8-sig", errors='ignore') as gd:
        for w in arr_accident_noun[step*3:]:
            gd.write(str(w)+", ")
        gd.close()

def manual_join():
    file_accident_noun1 = "traffic_accidents\\manual_filter\\1.txt"
    file_accident_noun2 = "traffic_accidents\\manual_filter\\2.txt"
    file_accident_noun3 = "traffic_accidents\\manual_filter\\3.txt"
    file_accident_noun4 = "traffic_accidents\\manual_filter\\4.txt"
    file_all_accident_noun = "traffic_accidents\\manual_filter\\all.txt"
    arr_accident_noun1 = get3000wordsFromNounFile(file_accident_noun1)
    arr_accident_noun2 = get3000wordsFromNounFile(file_accident_noun2)
    arr_accident_noun3 = get3000wordsFromNounFile(file_accident_noun3)
    arr_accident_noun4 = get3000wordsFromNounFile(file_accident_noun4)
    
    with open(file_all_accident_noun, "a", encoding="utf-8-sig", errors='ignore') as gd:
        for w in arr_accident_noun1:
            gd.write(str(w)+", ")
        for w in arr_accident_noun2:
            gd.write(str(w)+", ")
        for w in arr_accident_noun3:
            gd.write(str(w)+", ")
        for w in arr_accident_noun4:
            gd.write(str(w)+", ")
        gd.close()

def manual_shortenOrdinaryFile():
    arr_ordinary_noun = get3000wordsFromNounFile(FILE_3000_ORDINARY_NOUNS)
    with open(FILE_FILTERED_ORDINARY_NOUNS, "a", encoding="utf-8-sig", errors='ignore') as gd:
        for w in arr_ordinary_noun[:621]:
            gd.write(str(w)+", ")
        gd.close()
        
if __name__ == "__main__":
    main()