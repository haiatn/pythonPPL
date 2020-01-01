import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re


def preprocessing(data):
    data['tokens'] = data.apply(lambda row: word_tokenize(row.sentimentText.lower()), axis = 1)
    stopWords=set(stopwords.words('english'))
    data['tokens'] = [w.replace('#', '') for w in data['tokens'] if (not w in stopwords and not re.sub("@.","",w) and not re.sub("/^\d+$/","",w))]

def featureExtractions(preprocessedData):
    pass

def createClassifier():
    pass

def createPredictionFile(trainingData, model):
    pass

filePath=""
data=pd.read_csv(filePath,names=['sentimentText','Sentiment'])
preprocessedData = preprocessing(data)
model = createClassifier()
trainingData = featureExtractions(preprocessedData)
createPredictionFile(trainingData,model)

