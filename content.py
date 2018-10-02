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

FILE_3000_ACCIDENTS_NOUNS = "traffic_accidents\\3000_accident_nouns.txt"
FILE_3000_ORDINARY_NOUNS = "ordinary_contents\\3000_ordinary_nouns.txt"

NUMBER_NOUN_FILTERED = 3000
NUMBER_LINK_EACH_PAIR = 600

NUM_WORKERS = 20 #threading
urls = Queue()
urlsO = Queue()

class ContentHTML:    
    listAccidentURL = set()
    listOrdinaryURL = set()
    # 1.1. Get traffic accident contents
    @staticmethod
    def getContent(mode, spider, wordFile, urlFile, file):    
        print("D. Crawling 500 pages from 500_page_accidents.txt....")    
        ContentHTML.addLinkToQueue(urlFile, mode)        
        with open(file, "a", encoding="utf-8-sig", errors='ignore') as gd:
            ContentHTML.create_workersGetContent(mode, spider, gd)
            ContentHTML.create_jobs(mode)
            gd.close()
    
    @staticmethod
    def addLinkToQueue(urlFile, mode):
        tra_links = [line.rstrip('\n') for line in open(urlFile, encoding="utf8", errors='ignore')]
        for url in tra_links:
            if url[:3] == " + ":
                if ("youtube" in str(url[3:])):            
                    tmp = url[3:]
                else: 
                    tmp = url[3:].split('?')[0]
                if (mode == "accident"): 
                    ContentHTML.listAccidentURL.add(tmp) 
                elif (mode == "ordinary"):
                    ContentHTML.listOrdinaryURL.add(tmp)
            if (len(ContentHTML.listAccidentURL) >= NUMBER_LINK_EACH_PAIR or len(ContentHTML.listOrdinaryURL) >= NUMBER_LINK_EACH_PAIR):
                break
    @staticmethod   
    # 1.3. Make teacher data
    def create1000File(mode, listURLs):
        print("1.3.B. Make 1000 files (500 each folder corresponding 500 URLs)...") 
        arr_accident_noun = ContentHTML.get3000wordsFromNounFile(FILE_3000_ACCIDENTS_NOUNS)
        arr_ordinary_noun = ContentHTML.get3000wordsFromNounFile(FILE_3000_ORDINARY_NOUNS)
        for url in listURLs:
            ContentHTML.createFileCountNoun(mode, url, arr_accident_noun, arr_ordinary_noun)
    @staticmethod
    def saveContentEachPage(content, url, mode):
        fileName = urlToFileName(url)
        if (content is not None) and len(content.strip()) > 0:
            if mode == "accident":
                file_content_page = "traffic_accidents\\content_accidents_page_"+fileName+".txt"
                #print(urlToFileName(url))
                print("1.1.E. Get all the texts in each page...")
                print("1.1.F. Separate and extract all the noun words using the morphing analysis tool...")
            elif mode == "ordinary":
                file_content_page = "ordinary_contents\\content_ordinary_page_"+fileName+".txt"
                print("1.2.E. Get all the texts in each page...")
                print("1.2.F. Separate and extract all the noun words using the morphing analysis tool...")
            elif mode == "validation":
                print(content)
                file_content_page = "modeling\\validation\\content_"+fileName+".txt"
                print("3.B. Crawl it...")
        
            with open(file_content_page, "a", encoding="utf-8-sig") as gd:
                print(fileName+" writting txt... ")
                #print(content)
                gd.write(content)
                gd.close()
                print(fileName+" write OK")
                
    @staticmethod    
    def writeNounAndVerbToTxtfile(content, gd): 
        if ((content is not None) and len(content.strip()) > 0):
            tmp = ContentHTML.extractNoun(str(content))
            if len(tmp) > 0:
                gd.write(", ".join(tmp)+"\n")
                #print(", ".join(tmp))
    
    @staticmethod
    def extractNoun(content):
        arr_nouns = []
        if ((content is not None) and len(content.strip()) > 0):
            for word, pos in pos_tag(content):
                if ((pos == 'N' and isNoun(word))):
                    arr_nouns.append(word)
        return arr_nouns
    
    # Read 3000 accident noun from file
    @staticmethod
    def get3000wordsFromNounFile(file):
        if isFileExist(file):
            File = open(file, encoding="utf-8-sig", errors='ignore')
            accident_nouns = File.read().strip()
            arr_noun = re.split(', |\n',accident_nouns)[:-1]
            File.close()
            return arr_noun

    @staticmethod
    def createFileCountNoun(forwhich, url, arr_accident_noun, arr_ordinary_noun):
        csv_file_name = None
        csv_data = [[], []]
        fileName = urlToFileName(url)
        content = None
        if forwhich == "accident":
            # Read content file each page
            txtFile = "traffic_accidents\\content_accidents_page_"+fileName+".txt"
            if isFileExist(txtFile):
                File = open(txtFile, encoding="utf-8-sig", errors='ignore')
                content = File.read()
                csv_file_name = open("traffic_accidents//training_data//"+fileName+".csv", 'w', encoding="utf-8-sig", errors='ignore', newline='')
                File.close()
                #csv_data_accident = np.sort(csv_data_accident, axis=1)[:, ::-1]
        elif forwhich == "ordinary":        
            # Read content file each page
            txtFile = "ordinary_contents\\content_ordinary_page_"+fileName+".txt"
            if isFileExist(txtFile):
                File = open(txtFile, encoding="utf-8-sig", errors='ignore')
                content = File.read()
                csv_file_name = open("ordinary_contents//training_data//"+fileName+".csv", 'w', encoding="utf-8-sig", errors='ignore', newline='')
                File.close()
                #csv_data_ordinary = np.sort(csv_data_ordinary, axis=1)[:, ::-1]
        elif forwhich == "validation":
            # Read content file each page
            txtFile = "modeling\\validation\\content_"+fileName+".txt"
            if isFileExist(txtFile):
                File = open(txtFile, encoding="utf-8-sig", errors='ignore')
                content = File.read()
                File.close()
            csv_file_name = open("modeling\\validation\\"+fileName+".csv", 'w', encoding="utf-8-sig", errors='ignore', newline='')
        
			
        #csv_data = np.concatenate((csv_data_accident,csv_data_ordinary),axis=1)
        if ((content is not None) and len(content.strip()) > 0):
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
        elif forwhich == "validation":
            print('validation')
            csv_data = [[], []]
            csv_data[0] = arr_accident_noun + arr_ordinary_noun
            for x in range(len(arr_accident_noun)+len(arr_ordinary_noun)):
                csv_data[1].append(0)
        # write CSV file    
        #print(csv_data)
        
        if csv_file_name is not None:
            with csv_file_name:
                writer = csv.writer(csv_file_name)
                writer.writerows(csv_data)
                csv_file_name.close()
    
    @staticmethod
    def do_addContent(mode, spider, gd): 
        while True:
            if ("accident" == mode):
                url = urls.get() 
                content = spider.crawContent(url)
                if ((content is not None) and len(content.strip()) > 0):
                    ContentHTML.saveContentEachPage(content, url, mode)   
                    ContentHTML.writeNounAndVerbToTxtfile(content, gd)
                urls.task_done()
            else:
                url = urlsO.get()  
                content = spider.crawContent(url)
                if ((content is not None) and len(content.strip()) > 0):
                    ContentHTML.saveContentEachPage(content, url, mode)   
                    ContentHTML.writeNounAndVerbToTxtfile(content, gd)
                urlsO.task_done()
                
    @staticmethod
    def create_workersGetContent(mode, spider, gd):
        for i in range(NUM_WORKERS):
            t = threading.Thread(target=ContentHTML.do_addContent, args = (mode, spider, gd))
            t.daemon = True
            t.start()
          
    @staticmethod
    def create_jobs(mode):     
        if ("accident" == mode):
            for url in list(ContentHTML.listAccidentURL):
                urls.put(url)
            urls.join()
        else:
            for url in list(ContentHTML.listOrdinaryURL): 
                urlsO.put(url)
            urlsO.join()
