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
        B. Make 1000 files

        file name : URL
        file format :
        word1, word2, .................word3000, word3001, word3002,...............word6000
        count (word1), count(word2),.................................................................., word6000
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
from helper import makeLinkFromKeyword
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
        
def getTrafficAccidents():
    print("1.1.A. Read 50 VNese word related to traffic accidents from accidents.txt...")
    tra_words = [line.rstrip('\n') for line in open('traffic_accidents\\50_accidents_words.txt', encoding="utf8")]
    tra_words = tra_words[1:]    # bypass first row
    
    print("1.1.B. Google 50 words seperate (using Bing replace)...")
    is_process_whole_list = False
    spider = MySpider()
    for w in tra_words:
        link = makeLinkFromKeyword(w)
        spider.craw_link(link)
        if is_process_whole_list == False:
            c = input("press any key to continue craw next keyword, yy for whole list: ")
            if c.lower() == "yy":
                is_process_whole_list = True
        
    
    
    
if __name__ == "__main__":
    main()