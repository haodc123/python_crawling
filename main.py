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
from helper import makeLinkFromKeyword, isNoun
from underthesea import pos_tag
import requests
from collections import Counter
import csv

FILE_50_WORD_ACCIDENTS = "traffic_accidents\\50_accidents_words.txt"
FILE_500_PAGE_ACCIDENTS = "traffic_accidents\\500_page_accidents.txt"
FILE_ALL_ACCIDENTS_NOUNS = "traffic_accidents\\all_accident_nouns.txt"
FILE_3000_ACCIDENTS_NOUNS = "traffic_accidents\\3000_accident_nouns.txt"
NUMBER_NOUN_FILTERED = 3000

'''
Usage:
    type: python main.py --tra
    for 1.1. Get traffic accident contents
    type: python main.py --ord
    for 1.2. Get ordinary contents
'''
def main():
    args = sys.argv[1:]
    if args[0] == "--tra":   
        getTrafficAccidents()
    elif args[0] == "--ord":
        getOrdinaryContent()
    elif args[0] == "--test":
        test()
        
def getTrafficAccidents():
    print("1.1.A. Read 50 VNese word related to traffic accidents from accidents.txt...")
    tra_words = [line.rstrip('\n') for line in open(FILE_50_WORD_ACCIDENTS, encoding="utf8")]
    tra_words = tra_words[1:]    # bypass first row
    
    print("1.1.B. Google 50 words seperate (using Bing replace)...")
    spider = MySpider()
    for w in tra_words:
        link = makeLinkFromKeyword(w)
        spider.craw_link(link)
        
    print("1.1.D. Crawling 500 pages from 500_page_accidents.txt....")
    tra_links = [line.rstrip('\n') for line in open(FILE_500_PAGE_ACCIDENTS, encoding="utf8")]
    arr_500links = []
    for l in tra_links:
        if l[:3] == " + ":
            arr_500links.append(l[3:])
            content = spider.craw_content(l[3:])
            saveContentEachPage(content, len(arr_500links)-1)
    
    print("1.1.G. Count all the noun words together and align  them desc and pick up 3000 words...")
    countAndGetCommonNounFromFile(FILE_ALL_ACCIDENTS_NOUNS)

    print("1.3.B. Make 1000 files (500 each folder corresponding 500 URLs)...")
    for i in range(len(arr_500links)):
        create500FileCountNoun(i, FILE_3000_ACCIDENTS_NOUNS)

def saveContentEachPage(content, index):
    print("1.1.E. Get all the texts in each page...")
    with open("traffic_accidents\\content_accidents_page_"+str(index)+".txt", "a", encoding="utf-8") as gd:
        gd.write(content)

    print("1.1.F. Separate and extract all the noun words using the morphing analysis tool...")
    arr_nouns = extractNoun(str(content))

    for n in arr_nouns:
        with open(FILE_ALL_ACCIDENTS_NOUNS, "a", encoding="utf-8") as gd:
            gd.write(n+", ")

def extractNoun(content):
    arr_nouns = []
    for word,pos in pos_tag(content):
        if (pos == 'N' and isNoun(word)):
            arr_nouns.append(word)
    return arr_nouns

def create500FileCountNoun(index, filenameNoun):
    # Read content file each page
    File = open("traffic_accidents\\content_accidents_page_"+str(index)+".txt", encoding="utf-8")
    content = File.read()

    # Read 3000 noun from file
    File = open(filenameNoun, encoding="utf-8")
    nouns = File.read()
    arr_noun = nouns.split(", ")
	
	# Count noun in content
    csv_data = [[], []]
    for noun in arr_noun:
        count = str(content).count(noun)
        csv_data[0].append(noun)
        csv_data[1].append(count)

    #write CSV file
    csv_file_name = open("traffic_accidents//count_noun_accidents_page_"+str(index)+".csv", 'w', encoding="utf-8")
    with csv_file_name:
        writer = csv.writer(csv_file_name)
        writer.writerows(csv_data)

def countAndGetCommonNounFromFile(filename):
        File = open(filename, encoding="utf-8") #open file
        all_nouns = File.read()
        arr_all_noun = all_nouns.split(", ")
        nouns = Counter(arr_all_noun).most_common(NUMBER_NOUN_FILTERED)
        for word,num in nouns:
            with open(FILE_3000_ACCIDENTS_NOUNS, "a", encoding="utf-8") as gd:
                gd.write(word+", ")




def test():
    countAndGetCommonNounFromFile(FILE_ALL_ACCIDENTS_NOUNS)

def testExtractNoun(content):
        arr_nouns = []
        for word,pos in pos_tag(content):
            if (pos == 'N' and isNoun(word)):
                arr_nouns.append(word)
        return arr_nouns
		
if __name__ == "__main__":
    main()