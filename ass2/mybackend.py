import csv, sqlite3
from datetime import datetime
import math

class Database:
    def __init__(self):

        def countTableRows():
            return cur.execute("select count(*) from BikeShare").fetchone()

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS BikeShare ("
                         "TripDuration INT,"
                         "StartTime DATE,"
                         "StopTime DATE,"
                         "StartStationID INT,"
                         "StartStationName TEXT,"
                         "StartStationLatitude FLOAT,"
                         "StartStationLongitude FLOAT,"
                         "EndStationID INT,"
                         "EndStationName TEXT,"
                         "EndStationLatitude FLOAT,"
                         "EndStationLongitude FLOAT,"
                         "BikeID INT,"
                         "UserType TEXT,"
                         "BirthYear INT,"
                         "Gender INT,"
                         "TripDurationinmin INT)")
        if countTableRows()[0] == 0:
            with open('BikeShare.csv', 'rt') as fin:
                dr = csv.DictReader(fin)
                to_db = [(i['TripDuration'], i['StartTime'], i['StopTime'], i['StartStationID'], i['StartStationName'], i['StartStationLatitude'], i['StartStationLongitude'], i['EndStationID'], i['EndStationName'], i['EndStationLatitude'], i['EndStationLongitude'], i['BikeID'], i['UserType'], i['BirthYear'], i['Gender'], i['TripDurationinmin']) for i in dr]
            cur.executemany("INSERT INTO BikeShare (TripDuration, StartTime, StopTime, StartStationID, StartStationName, StartStationLatitude, StartStationLongitude, EndStationID, EndStationName, EndStationLatitude, EndStationLongitude, BikeID, UserType, BirthYear, Gender, TripDurationinmin)"
                            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
        conn.commit()
        conn.close()

    def getRecommendations(self, currentLocation, spendTime, numRecommendations):
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        res = cur.execute("select * from BikeShare "
                          "where StartStationName like '" + currentLocation +

                          "' and TripDurationinmin <= " + str(spendTime)
                          # "' and EndStationName like '" + currentLocation +
                          #" limit " + str(numRecommendations)
                          ).fetchall()
        conn.close()
        return self.orderByMostRecommended(res,self.ratingOption1,spendTime,numRecommendations);

    def orderByMostRecommended(self,res,ratingFunc,spendTime,numRecommendations):
        resultsWithRatings={}
        for row in res:
            resultsWithRatings[row[8]]=ratingFunc(row,spendTime)
        return sorted(resultsWithRatings.items(), key=lambda item: item[1],reverse=True)[:int(numRecommendations)]

    def ratingOption1(self, row,spendTime):
        rowStartTime=row[1]
        rowTripDurationinmin = int(row[15])
        rowStartStationLatitude = row[5]
        rowEndStationLatitude = row[9]
        rowStartStationLongitude = row[6]
        rowEndStationLongitude = row[10]

        #each normalize create number in [0,1] where the highest is the best
        rowHourInString=rowStartTime.split(" ")[1].split(":")[0]
        deltaHour=abs(datetime.now().hour - int(rowHourInString))
        normalizedDeltaHour= 1 - 2*(deltaHour/24)
        deltaSpendTime= abs(rowTripDurationinmin-int(spendTime))
        normalizedDeltaSpendTime=  4/(4+deltaSpendTime)
        distance=math.sqrt( (rowStartStationLatitude-rowEndStationLatitude)**2 + (rowStartStationLongitude-rowEndStationLongitude)**2) #auclidian distnace
        normalizedDistance=1/(1+distance)
        return normalizedDeltaHour+normalizedDeltaSpendTime+normalizedDistance


def checkUserInput(userStart, userTime, userAmount):
    if userStart=="" or userStart==None:
        return "you did not insert your starting point"
    if userTime=="" or userTime==None:
        return "you did not insert the time you want to spend"
    if userAmount == "" or userAmount == None:
        return "you did not insert the number of wanted location recommendations"
    try:
        userTime=int(userTime)
    except ValueError:
        return "please enter spending time in minutes by numbers only"
    try:
        userAmount=int(userAmount)
    except ValueError:
        return "please enter the number for location recommendation amount"

    if(userTime<1):
        return "we don't offer locations for this riding time"
    if (userAmount < 1):
        return "the number of locations is invalid"
    return None



#db = Database()
#print(db.getRecommendations("Hilltop", 6, 5))



