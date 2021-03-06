# Is Traffic Accident ?

Detecting a link is related to traffic accident or not (in Vietnamese)<br/>
Developing for Demostration of Back Khoa Seminar 10/2018

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

```
- Anaconda 5.x (Python 3)
- Underthesea
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
- On Windows:
 1. Download and install Anaconda 5.x (already include python 3)
 2. pip install underthesea
 
- On Ubuntu:
 1. set default python3 on ubuntu
https://askubuntu.com/questions/320996/how-to-make-python-program-command-execute-python-3
 2. install pip3 for python3
sudo apt-get update
sudo apt-get -y install python3-pip
 3. install anaconda 
https://www.rosehosting.com/blog/how-to-install-the-anaconda-python-distribution-on-ubuntu-16-04/
 4. install Underthesea library by pip3
pip3 install underthesea
```

## How it's work

Using Random Forest to learn (from teacher data) and prediction.

```
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
    B. Model using random forest
3.Verification
    A. Input URL
    B. Crawl it
    C. Separate and extract all the noun words using the morphing analysis tool
    D. Count all the noun words
    E. Make CSV file
    F. Verify
```

## Running the tests

Explain how to run the tests for this program

```
Usage:
    Validate link
        type: python main.py --model <link>
            for 3. Validation a link is releated to traffic accident or not (via regressor method)
        type: python main.py --model2 <link>
            for 3. Validation a link is releated to traffic accident or not (via classifier method)
```
