import csv, sqlite3

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
                          "' and EndStationName like '" + currentLocation +
                          "' and TripDurationinmin <= " + str(spendTime) +
                          " limit " + str(numRecommendations)).fetchall()
        conn.close()
        return res


db = Database()
#print(db.getRecommendations("Hilltop", 6, 5))



