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
from spider import MySpider
from helper import *
from content import ContentHTML
import requests
from collections import Counter
import csv
import time
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
        #call get content and count Noun,
        '''
        TODO: You need to implement 
            1. getContent static function to get text content from links and save each file for each page
              	(E. Get all the texts in each page.)
            2. get all noun in all page content you get and save to
                FILE_ALL_ACCIDENTS_NOUNS
               	(F. Separate and extract all the noun words using the morphing analysis tool.)
        '''
        ContentHTML.getContent()
        ContentHTML.getAllNoun()
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
        #call get content and count Noun,
        '''
        TODO: You need to implement 
            1. getContent static function to get text content from links and save each file for each page
              	(E. Get all the texts in each page.)
            2. get all noun in all page content you get, and save to
                FILE_ALL_ORDINARY_NOUNS
               	(F. Separate and extract all the noun words using the morphing analysis tool.)
        '''
        ContentHTML.getContent()
        ContentHTML.getAllNoun()

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
    elif args[0] == "--test":
        test()
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
    
def test():
    print("a")
        
if __name__ == "__main__":
    main()