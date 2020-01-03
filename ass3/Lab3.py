import nltk
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from string import punctuation
from sklearn import model_selection
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
# nltk.download('punkt')
# nltk.download('stopwords')

def preprocessing(data):
    data['tokens'] = data.apply(lambda row: word_tokenize(row['SentimentText'].lower()), axis=1)
    stopWords = set(stopwords.words('english'))
    stopWords.difference(["yes","no"])
    stopWords.add("...")
    # data['tokens'] = data.apply(lambda row : [w.replace('#', '') for w in row['tokens'] if
    #                   not w in stopWords and not re.sub("@.", "", w) and not re.sub("/^\d+$/", "", w)], axis=1)
    data['tokens']=data.apply(lambda row: cleanTokens(row['tokens'], stopWords), axis=1)
    return data

def cleanTokens(tokens, stopWords):
    intRegex = re.compile(r'(?:(?<=^)|(?<=\s))\d+(?=\s|$)')
    tagRegex = re.compile(r'^@')
    cleanTokens = [w.replace('#', '') for w in tokens if not w in stopWords and (
        not intRegex.match(w)) and (not w in punctuation)]  # if  (not w in stopWords)  and (not re.sub("/^\d+$/", "", w))
    tokensWithoutTags = []
    for i in range(len(cleanTokens)):
        if (not tagRegex.match(cleanTokens[i])) and (i != 0 and not tagRegex.match(cleanTokens[i - 1])):
            tokensWithoutTags.append(cleanTokens[i])
    return tokensWithoutTags

def featureExtractions(preprocessedData):
    wordCounter={0:{},1:{}}
    data.apply(lambda row: addToCounter(row,wordCounter), axis=1)
    wordCounter = {0: sorted(wordCounter[0].items(), key=lambda kv: -kv[1]), 1: sorted(wordCounter[1].items(), key=lambda kv: -kv[1])}
    s=""
    for i in range(100):
        s=s+str(wordCounter[0][i][0])+","+str(wordCounter[0][i][1])+","+str(wordCounter[1][i][0])+","+str(wordCounter[0][i][1])+"\n"
    with open("popularWords.csv", "w") as f:
        f.write(s)

def addToCounter(row,wordCounter):
    for token in row['tokens']:
        if token not in wordCounter[row["Sentiment"]].keys():
            wordCounter[row["Sentiment"]][token]=1
        else:
            wordCounter[row["Sentiment"]][token] = wordCounter[row["Sentiment"]][token]+1

def createClassifiers():
    models=[]
    models.append("knn",KNeighborsClassifier())
    models.append("decision tree", DecisionTreeClassifier())
    models.append("naive bayes", GaussianNB())
    models.append("SVM", SVC())
    return models

def calculateModelsAccuracy(trainingData, models):
    results = []
    for name,model in models:
        crossValidition=model_selection.cross_val_score(model,X_train,Y_train,cv=10,scoring="accuracy")
        results.append(crossValidition)
        print(name+": "+crossValidition.mean())
def predictionsToTestFile(model,X_train, X_validation, Y_train):
        model.fit(X_train,Y_train)
        predictions=model.predict(X_validation)
        s=""
        for i in range(len(predictions)):
            s=s+str(i)+","+predictions[i]+"\n"
        with open("predictions.csv", "w") as f:
            f.write(s)




filePath = "Train.csv"
data = pd.read_csv(filePath,header=0, engine='python').head(50000) #so we can check on last 30000 as validation
preprocessedData = preprocessing(data)
trainingData = featureExtractions(preprocessedData)


# X = trainingData.iloc[:, 0:4] #TODO fix to real indexes
# Y = trainingData.iloc[:, 4]
# validation_size = 0.20
# seed = 7
# X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size, random_state=seed)

models = createClassifiers()
#calculateModelsAccuracy(X_train, Y_train, models)
#predictionsToTestFile(models[0],X_train, X_validation, Y_train) #TODO fix to the right model selected







