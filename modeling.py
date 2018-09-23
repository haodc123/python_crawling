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
        self.train_np_features = None
        self.train_np_labels = None
        self.test_np_features = None
        self.test_np_labels = None
        self.method = method
        if method == "regressor":
            self.rf = None
        elif method == "classifier":
            self.dt = None

    # 2. Modeling using RandomForest
    def createModel(self):
        # create model-input standard data file
        if not isFileExist(FILE_STANDARD_DATA):
            self.createStandarDataFile()

        self.prepareInputData(FILE_STANDARD_DATA)
        if self.method == "regressor":
            self.trainingModelRegressor()
        elif self.method == "classifier":
            self.trainingModelClassifier()

    def prepareInputData(self, fileInput):
        features = pd.read_csv(fileInput)
        
        labels = features['is_traffic_accident']
        np_labels = np.array(labels)
        features= features.drop('is_traffic_accident', axis = 1)
        np_features = np.array(features)

        feature_list = list(features.columns)

        self.train_np_features, self.test_np_features, self.train_np_labels, self.test_np_labels = train_test_split(np_features, np_labels, test_size = 0.25, random_state = 42)
        
    def trainingModelRegressor(self):
        self.rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)
        self.rf.fit(self.train_np_features, self.train_np_labels);

    def trainingModelClassifier(self):
        self.dt = DecisionTreeClassifier(max_depth=3)
        self.dt.fit(self.train_np_features, self.train_np_labels);

    def validateModel(self, link):
        validationFile = "modeling\\validation\\"+urlToFileName(link)+".csv"
        self.createModel()
        print("create model...done")
        validation_features = pd.read_csv(validationFile)
        np_validation_features = np.array(validation_features)

        if self.method == "regressor":
            predictions = self.rf.predict(np_validation_features)
        elif self.method == "classifier":
            predictions = self.dt.predict(np_validation_features)
        
        print('Predictions: ', str(predictions))

    def testModelRegressor(self):
        predictions = self.rf.predict(self.test_np_features)
        # Calculate the absolute errors
        errors = abs(predictions - self.test_np_labels)
        # Print out the mean absolute error (mae)
        print('Mean Absolute Error:', round(np.mean(errors), 2))

    def testModelClassifier(self):
        predictions = self.dt.predict(self.test_np_features)
        # Calculate the absolute errors
        errors = abs(predictions - self.test_np_labels)
        # Print out the mean absolute error (mae)
        print('Mean Absolute Error:', round(np.mean(errors), 2))

    def createStandarDataFile(self):
        #csvFiles = []
        dirAccident = './traffic_accidents/training_data'
        dirOrdinary = './ordinary_contents/training_data'
        dirAccidentFiles = os.listdir(dirAccident)
        dirOrdinaryFiles = os.listdir(dirOrdinary) 
        line = 0
        with open(FILE_STANDARD_DATA, 'w', encoding="utf-8", newline='') as gd:
            writer = csv.writer(gd, quoting=csv.QUOTE_NONE, delimiter='|', quotechar='|',escapechar='\\')
            for file in dirAccidentFiles:
                if ('.csv' in file):
                    line = self.writeData(file, dirAccident, writer, line)                     
            for file in dirOrdinaryFiles:
                if ('.csv' in file):
                    self.writeData(file, dirOrdinary, writer, line)            
            
    def writeData(self, file, folder, writer, line):
        #print(file)
        tmp = []
        with open(folder+"//"+file, 'r', encoding='utf-8') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='\n', quotechar='|')
            for i,x in enumerate(spamreader):                            
                if (0 == line):                    
                    tmp.append([''.join(x)+',is_traffic_accident'])
                    #writer.writerows(''.join(x))
                    line += 1
                elif (0 != line and i > 0):
                    if ('ordinary' in folder):
                        tmp.append([''.join(x)+',0'])
                    else:
                        tmp.append([''.join(x)+',1'])      
                    
            writer.writerows(tmp)  
        return 1

    

    '''def createStandarDataFile(self, filenameAccidentNoun, filenameOrdinaryNoun):
        # Read 3000 accident noun from file
        File = open(filenameAccidentNoun, encoding="utf-8", errors='ignore')
        accident_nouns = File.read()
        arr_header_file = accident_nouns.split(", ")
        # Read 3000 ordinary noun from file
        File = open(filenameOrdinaryNoun, encoding="utf-8", errors='ignore')
        ordinary_nouns = File.read()
        arr_header_file.append(ordinary_nouns.split(", "))
        arr_header_file.append("is_traffic_accident")
        num_column = len(arr_header_file)

        # Read all csv file to get count number of each noun
        home_path = getCurrentPath()
        arr_accident_csv = getAllFileInPath("csv", home_path+'\\traffic_accidents\\training_data')
        goToPath(home_path)
        arr_ordinary_csv = getAllFileInPath("csv", home_path+'\\ordinary_contents\\training_data')
        goToPath(home_path)
        num_row = len(arr_accident_csv) + len(arr_ordinary_csv) + 1

        csv_file_name = open(FILE_STANDARD_DATA, 'w', encoding="utf-8", errors='ignore')
        
        csv_data = [[0] * num_column] * num_row
        csv_data[0] = arr_header_file

        row = 1
        for filename in arr_accident_csv:
            arr_accident_line = [line.rstrip('\n') for line in open("traffic_accidents\\training_data\\"+filename, encoding="utf8")]
            arr_accident_num = arr_accident_line[39].split(",")
            arr_accident_num.append("1") # is_traffic_accident = 1
            csv_data[row] = arr_accident_num
            row += 1
        for filename in arr_ordinary_csv:
            arr_ordinary_line = [line.rstrip('\n') for line in open("ordinary_contents\\training_data\\"+filename, encoding="utf8")]
            arr_ordinary_num = arr_ordinary_line[39].split(",")
            arr_ordinary_num.append("0") # is_traffic_accident = 0
            csv_data[row] = arr_ordinary_num
            row += 1

        # write CSV file
        with csv_file_name:
            writer = csv.writer(csv_file_name)
            writer.writerows(csv_data)'''