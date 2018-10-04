import csv
from helper import *
import pandas as pd
import numpy as np
import glob
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn import tree

FILE_50_WORD_ACCIDENTS = "traffic_accidents\\50_accidents_words.txt"
FILE_500_PAGE_ACCIDENTS = "traffic_accidents\\500_page_accidents.txt"
FILE_ALL_ACCIDENTS_NOUNS = "traffic_accidents\\all_accident_nouns.txt"
FILE_3000_ACCIDENTS_NOUNS = "traffic_accidents\\3000_accident_nouns.txt"

FILE_50_ALEXA_ORDINARY_LINK = "ordinary_contents\\50_alexa_ordinary.txt"
FILE_500_PAGE_ORDINARY = "ordinary_contents\\500_page_ordinary.txt"
FILE_ALL_ORDINARY_NOUNS = "ordinary_contents\\all_ordinary_nouns.txt"
FILE_3000_ORDINARY_NOUNS = "ordinary_contents\\3000_ordinary_nouns.txt"

FILE_STANDARD_DATA = "modeling\\standard_data.csv"

class MyModeling(object):

    def __init__(self, method):
        

    # 2. Modeling using RandomForest
    def createModel(self):
        
    def prepareInputData(self, fileInput):
        
    def trainingModelRegressor(self):
        
    def trainingModelClassifier(self):
        
    def validateModel(self, link):
        
    def testModelRegressor(self):
        
    def testModelClassifier(self):
        
    def createStandarDataFile(self):
        