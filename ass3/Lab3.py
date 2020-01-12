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
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
nltk.download('punkt')
nltk.download('stopwords')
'''
process the given data before the classification
first of all tokenize the given data
then remove stop words, and clean the words
:param data - the overall data that was read from the train csv
:return the same data with addition column of the tokenized text
'''
def preprocessing(data):
    data['tokens'] = data.apply(lambda row: word_tokenize(row['SentimentText'].lower()), axis=1)
    stopWords = set(stopwords.words('english'))
    stopWords.difference(["yes","no","not",'against'])
    stopWords.update(["...","like","'m","u","know","'re","'ll","one","'s",""])
    data['tokens']=data.apply(lambda row: cleanTokens(row['tokens'], stopWords), axis=1)
    data['smileys']=data.apply(lambda row: findSmileys(row['SentimentText']), axis=1)
    for index, row in data.iterrows():
        row['tokens'].extend([row['smileys']])
    return data

'''
clean the given tokens from stopwords, symbols and punctuation (like #, @)
:param tokens - a list that contains the initial text separated into tokens
:param stopWords - the updated list of words that will be cleaned from the final text
:return a list of the final tokens
'''
def cleanTokens(tokens, stopWords):
    intRegex = re.compile(r'(?:(?<=^)|(?<=\s))\d+(?=\s|$)')
    tagRegex = re.compile(r'^@.*')
    myPunctuation=punctuation.replace('@', '')
    cleanTokens = [w.replace('#', '') for w in tokens if not w in stopWords and (not intRegex.match(w)) and (not w in myPunctuation)]
    tokensWithoutTags = []
    stemmer=PorterStemmer()
    for i in range(len(cleanTokens)):
        if (i==0 and not tagRegex.match(cleanTokens[i])) or (i!= 0 and not tagRegex.match(cleanTokens[i - 1])):
            tokensWithoutTags.append(stemmer.stem(cleanTokens[i]))
    return tokensWithoutTags

def findSmileys(text):
  happySmiles=[":)","(:","(-:",":-)",";)","(;", ":(p)"]
  sadSmiles=[":(","):",")-:",":-(",";(",");"]
  for smile in happySmiles:
    if smile in text:
      return "happysmile"
  for smile in sadSmiles:
    if smile in text:
      return "sadsmile"
  return ""

'''
extract features of the given processed data before the classification (this function must be called after the original data proccesed)
the extracted features are: tf*idf
:param preprocessedData - the processed data (contains 3 columns, 1-Sentiment, 2-SentimentText, 3-tokenized SentimentText)
:return 3 parameters, the first is the training set as an array, the second is the array for each document in
training set and the vectorizer for later use
'''
def featureExtractions(preprocessedData):
    corpus=[  " ".join(record) for record in preprocessedData['tokens']]
    Y=[ sentiment for sentiment in preprocessedData['Sentiment']]
    vectorizer = TfidfVectorizer(min_df=0.0005)
    X = vectorizer.fit_transform(corpus)
    return X.toarray(),Y,vectorizer

'''
:return a list of models that we want to evaluate
'''
def createClassifiers():
    models=[]
    #models.append(("knn",KNeighborsClassifier()))
    #models.append(("decision tree", DecisionTreeClassifier(min_samples_leaf=200)))
    models.append(("logistic regression",LogisticRegression(random_state=0)))
    #models.append(("logistic regression",LogisticRegression(random_state=0,penalty='elasticnet')))
    #models.append(("logistic regression",LogisticRegression(random_state=0,penalty='none')))
    #models.append(("gsboost",GradientBoostingClassifier()))
    #models.append(("naive bayes", GaussianNB()))
    #models.append(("SVM", SVC(gamma="scale")))
    return models


'''
evaluate the models in the given models list with the given X and Y data
print the accurancy, precision, recall of each of the models
:param X - array of documents to be trained on
:param Y - array of target classifications that matches X positions
:param models - a list of models that will be evaluated
'''
def calculateModelsAccuracy(X,Y, models):
    results = []
    print("start training models")
    for name,model in models:
        crossValidition=model_selection.cross_validate(model,X,Y,cv=10,scoring=["accuracy","precision","recall"])
        results.append(crossValidition)
        print(name+": ",crossValidition["test_accuracy"].mean(),crossValidition["test_precision"].mean(),crossValidition["test_recall"].mean())

'''
predict the given test data according to the given model
finally print to a csv file which contains 2 columns, 
the first is the ID of the tested row and the second is the predicted sentiment
:param model - the chosen model for the prediction 
:param X - array of documents to be trained on
:param Y - array of target classifications that matches X positions
:param test - the test data to be predicted in the form the same as X
'''
def predictionsToTestFile(model,X,Y,vectorizer,name):
        test = pd.read_csv("Test.csv", header=0, engine='python')
        preprocessedData = preprocessing(test)
        testVector=vectorizer.transform([ " ".join(tokenList) for tokenList in preprocessedData['tokens']]).toarray()
        model.fit(X,Y)
        predictions=model.predict(testVector)
        s="ID,Sentiment\n"
        for i in range(len(predictions)):
            s=s+str(i)+","+str(predictions[i])+"\n"
        with open("predictions"+name+".csv", "w") as f:
            f.write(s)

filePath = "Train.csv"
data = pd.read_csv(filePath,header=0, engine='python')#.head(10000)
preprocessedData = preprocessing(data)
X,Y,vectorizer = featureExtractions(preprocessedData)
models = createClassifiers()
calculateModelsAccuracy(X,Y, models)
#predictionsToTestFile(models[0][1],X,Y,vectorizer,"regular")
predictionsToTestFile(models[0][1],X,Y,vectorizer,"1")
predictionsToTestFile(models[1][1],X,Y,vectorizer,"2")
predictionsToTestFile(models[2][1],X,Y,vectorizer,"3")