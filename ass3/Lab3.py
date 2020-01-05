import nltk
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import re
from string import punctuation
from sklearn import model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
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
    stopWords.update(["...","'m","like","u","know","'re","'ll","one","'s",""])
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
    stemmer=PorterStemmer()
    for i in range(len(cleanTokens)):
        if (not tagRegex.match(cleanTokens[i])) and (i != 0 and not tagRegex.match(cleanTokens[i - 1])):
            tokensWithoutTags.append(stemmer.stem(cleanTokens[i]))
    return tokensWithoutTags

def featureExtractions(preprocessedData):
    print("start feature extractions")
    corpus=[ " ".join(tokenList) for tokenList in preprocessedData['tokens']]
    Y=[ sentiment for sentiment in preprocessedData['Sentiment']]
    vectorizer = TfidfVectorizer(max_features=1000, min_df=0.01)
    X = vectorizer.fit_transform(corpus)
    print("finished feature extractions")
    return X,Y

def createFileOfFrequantWords(preprocessedData):
    wordCounter = {0: {}, 1: {}}
    data.apply(lambda row: addToCounter(row, wordCounter), axis=1)
    wordCounter = {0: sorted(wordCounter[0].items(), key=lambda kv: -kv[1]),
                   1: sorted(wordCounter[1].items(), key=lambda kv: -kv[1])}
    s = ""
    for i in range(100):
        s = s + str(wordCounter[0][i][0]) + "," + str(wordCounter[0][i][1]) + "," + str(
            wordCounter[1][i][0]) + "," + str(wordCounter[0][i][1]) + "\n"
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
    models.append(("knn",KNeighborsClassifier()))
    models.append(("decision tree", DecisionTreeClassifier()))
    models.append(("naive bayes", GaussianNB()))
    models.append(("SVM", SVC()))
    return models

def calculateModelsAccuracy(X,Y, models):
    results = []
    print("start training models")
    for name,model in models:
        #10 cross validation
        #crossValidition=model_selection.cross_val_score(model,X,Y,cv=10,scoring=["accuracy","precision","recall"])
        crossValidition=model_selection.cross_validate(model,X,Y,cv=10,scoring=["accuracy","precision","recall"])
        results.append(crossValidition)
        print(name+": ",crossValidition["test_accuracy"],crossValidition["test_precision"],crossValidition["test_recall"])


def predictionsToTestFile(model,X,Y,test):
        model.fit(X,Y)
        predictions=model.predict(test)
        s=""
        for i in range(len(predictions)):
            s=s+str(i)+","+predictions[i]+"\n"
        with open("predictions.csv", "w") as f:
            f.write(s)




filePath = "Train.csv"
data = pd.read_csv(filePath,header=0, engine='python')
preprocessedData = preprocessing(data)
X,Y = featureExtractions(preprocessedData)

models = createClassifiers()
calculateModelsAccuracy(X,Y, models)
#predictionsToTestFile(models[0],X,Y,test) #TODO fix to the right model selected







