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
from helper import makeLinkFromKeyword, isNoun, urlToFileName
from underthesea import pos_tag
import requests
from collections import Counter
import csv

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
    if args[0] == "--tra":        # 1.1. Get traffic accident contents
        getTrafficAccidents()
    elif args[0] == "--ord":      # 1.2. Get ordinary contents
        getOrdinaryContent()
    elif args[0] == "--file":     # 1.3. Make teacher data
        arr_500_accident_link = get500LinksFromFile("accident")
        arr_500_ordinary_link = get500LinksFromFile("ordinary")
        create1000File(arr_500_accident_link, arr_500_ordinary_link)
    elif args[0] == "--mix":      # 1.1 + 1.2 + 1.3. Make teacher data
        arr_500_accident_link = getTrafficAccidents()
        arr_500_ordinary_link = getOrdinaryContent()
        create1000File(arr_500_accident_link, arr_500_ordinary_link)
    elif args[0] == "--test":
        test()

# 1.1. Get traffic accident contents
def getTrafficAccidents():
    print("1.1.A. Read 50 VNese word related to traffic accidents from accidents.txt...")
    tra_words = [line.rstrip('\n') for line in open(FILE_50_WORD_ACCIDENTS, encoding="utf8")]
    tra_words = tra_words[1:]    # bypass first row
    
    print("1.1.B. Google 50 words seperate (using Bing replace)...")
    spider = MySpider()
    for w in tra_words:
        link = makeLinkFromKeyword(w)
        spider.craw_link(link, "accident")
        
    print("1.1.D. Crawling 500 pages from 500_page_accidents.txt....")
    tra_links = [line.rstrip('\n') for line in open(FILE_500_PAGE_ACCIDENTS, encoding="utf8")]
    arr_500links = []
    for l in tra_links:
        if l[:3] == " + ":
            if len(arr_500links) >= NUMBER_LINK_EACH_PAIR:
                break
            arr_500links.append(l[3:])
            content = spider.craw_content(l[3:])
            saveContentEachPage(content, len(arr_500links)-1, "accident")
    
    print("1.1.G. Count all the noun words together and align  them desc and pick up 3000 words...")
    countAndGetCommonNounFromFile("accident")
    return arr_500links


# 1.2. Get ordinary contents
def getOrdinaryContent():
    print("1.2.A. List up top 50 Vietnamese sites. using similarweb and/or Alexa...")
    alexa_links = [line.rstrip('\n') for line in open(FILE_50_ALEXA_ORDINARY_LINK, encoding="utf8")]
    alexa_links = alexa_links[1:]    # bypass first row
    
    print("1.2.B. Crawling 10 pages for each site....")
    spider = MySpider()
    for l in alexa_links:
        spider.craw_link(l, "ordinary")
        
    print("1.2.D. Crawling 500 pages from 500_page_ordinary.txt....")
    ord_links = [line.rstrip('\n') for line in open(FILE_500_PAGE_ORDINARY, encoding="utf8")]
    arr_500links = []
    for l in ord_links:
        if l[:3] == " + ":
            if len(arr_500links) >= NUMBER_LINK_EACH_PAIR:
                break
            arr_500links.append(l[3:])
            content = spider.craw_content(l[3:])
            saveContentEachPage(content, len(arr_500links)-1, "ordinary")
    
    print("1.2.G. Count all the noun words together and align  them desc and pick up 3000 words...")
    countAndGetCommonNounFromFile("ordinary")
    return arr_500links


# 1.3. Make teacher data
def create1000File(arr_500_accident_link, arr_500_ordinary_link):
    print("1.3.B. Make 1000 files (500 each folder corresponding 500 URLs)...")
    # For 500 Accident
    for i in range(NUMBER_LINK_EACH_PAIR):
        create500FileCountNoun("accident", i, FILE_3000_ACCIDENTS_NOUNS, FILE_3000_ORDINARY_NOUNS, arr_500_accident_link)
    # For 500 Ordinary
    for i in range(NUMBER_LINK_EACH_PAIR):
        create500FileCountNoun("ordinary", i, FILE_3000_ACCIDENTS_NOUNS, FILE_3000_ORDINARY_NOUNS, arr_500_ordinary_link)

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


def saveContentEachPage(content, index, mode):
    if mode == "accident":
        file_content_page = "traffic_accidents\\content_accidents_page_"+str(index)+".txt"
        file_all_noun = FILE_ALL_ACCIDENTS_NOUNS
        print("1.1.E. Get all the texts in each page...")
        print("1.1.F. Separate and extract all the noun words using the morphing analysis tool...")
    elif mode == "ordinary":
        file_content_page = "ordinary_contents\\content_ordinary_page_"+str(index)+".txt"
        file_all_noun = FILE_ALL_ORDINARY_NOUNS
        print("1.2.E. Get all the texts in each page...")
        print("1.2.F. Separate and extract all the noun words using the morphing analysis tool...")

    with open(file_content_page, "a", encoding="utf-8", errors='ignore') as gd:
        gd.write(content)

    arr_nouns = extractNoun(str(content))

    for n in arr_nouns:
        with open(file_all_noun, "a", encoding="utf-8", errors='ignore') as gd:
            gd.write(n+", ")

def extractNoun(content):
    arr_nouns = []
    for word,pos in pos_tag(content):
        if (pos == 'N' and isNoun(word)):
            arr_nouns.append(word)
    return arr_nouns

def create500FileCountNoun(forwhich, index, filenameAccidentNoun, filenameOrdinaryNoun, arr_500_link):
    # Read 3000 accident noun from file
    File = open(filenameAccidentNoun, encoding="utf-8", errors='ignore')
    accident_nouns = File.read()
    arr_accident_noun = accident_nouns.split(", ")
    # Read 3000 ordinary noun from file
    File = open(filenameOrdinaryNoun, encoding="utf-8", errors='ignore')
    ordinary_nouns = File.read()
    arr_ordinary_noun = ordinary_nouns.split(", ")

    if forwhich == "accident":
        # Read content file each page
        File = open("traffic_accidents\\content_accidents_page_"+str(index)+".txt", encoding="utf-8", errors='ignore')
        content = File.read()
        csv_file_name = open("traffic_accidents//"+urlToFileName(arr_500_link[index])+".csv", 'w', encoding="utf-8", errors='ignore')
    elif forwhich == "ordinary":
        # Read content file each page
        File = open("ordinary_contents\\content_ordinary_page_"+str(index)+".txt", encoding="utf-8", errors='ignore')
        content = File.read()
        csv_file_name = open("ordinary_contents//"+urlToFileName(arr_500_link[index])+".csv", 'w', encoding="utf-8", errors='ignore')

    # Count noun in content
    csv_data = [[], []]
    for noun in arr_accident_noun:
        count = str(content).count(noun)
        csv_data[0].append(noun)
        csv_data[1].append(count)
    for noun in arr_ordinary_noun:
        count = str(content).count(noun)
        csv_data[0].append(noun)
        csv_data[1].append(count)
    # write CSV file
    with csv_file_name:
        writer = csv.writer(csv_file_name)
        writer.writerows(csv_data)

def countAndGetCommonNounFromFile(mode):
    if mode == "accident":
        file_all_noun = FILE_ALL_ACCIDENTS_NOUNS
        file_3000_noun = FILE_3000_ACCIDENTS_NOUNS
    elif mode == "ordinary":
        file_all_noun = FILE_ALL_ORDINARY_NOUNS
        file_3000_noun = FILE_3000_ORDINARY_NOUNS

    File = open(file_all_noun, encoding="utf-8", errors='ignore')
    all_nouns = File.read()
    arr_all_noun = all_nouns.split(", ")
    arr_nouns = Counter(arr_all_noun).most_common(NUMBER_NOUN_FILTERED)
        
    for word,num in arr_nouns:
        with open(file_3000_noun, "a", encoding="utf-8", errors='ignore') as gd:
            gd.write(word+", ")




def test():
    File = open("traffic_accidents\\content_accidents_page_12.txt", encoding="utf-8", errors='ignore')
    c = File.read()
    print(len(str(c)))


        
if __name__ == "__main__":
    main()