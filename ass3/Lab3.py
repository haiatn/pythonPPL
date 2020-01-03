import nltk
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

nltk.download('punkt')
nltk.download('stopwords')


def preprocessing(data):
    print(data.head(30))
    data['tokens'] = data.apply(lambda row: word_tokenize(row['SentimentText'].lower()), axis=1)
    print(data.head(30))
    stopWords = set(stopwords.words('english'))
    data['tokens'] = data.apply(lambda row : [w.replace('#', '') for w in row if
                      not w in stopWords and not re.sub("@.", "", w) and not re.sub("/^\d+$/", "", w)], axis=1)
    print(data.head(30))


def featureExtractions(preprocessedData):
    pass


def createClassifier():
    pass


def createPredictionFile(trainingData, model):
    pass


filePath = "C:/Users/alina/Downloads/Train.csv/Train.csv"
data = pd.read_csv(filePath, engine='python', names=['Sentiment', 'SentimentText'])
preprocessedData = preprocessing(data)
model = createClassifier()
trainingData = featureExtractions(preprocessedData)
createPredictionFile(trainingData, model)
