from miniProject import spotifyChartsAPI
import spotipy
import os
import sqlite3
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

'''
this class works with API's and is used to build the database. It takes about 4 hours.
we create a database of songs and artists from the 1-10-18 to 31-10-19 listening patterns of 
Israeli citizens. 
'''

# authentication with spotify. Note that this is confidential
os.environ["SPOTIPY_CLIENT_ID"] = "1b73550cbd9144149ec64aff3a6fc3fc"
os.environ["SPOTIPY_CLIENT_SECRET"] = "aa0fa9dbf7de4ab7b653f15da895c3e3"
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

'''
input:
:param table- the table to take genres from. Because we create two table we must specify if 'songs' or 'normalizedSongs'
output:
:returns list of the string names of genres that in the table given
'''
def getGenres(table):
    with sqlite3.connect("spotifyGraphDB.sqlite") as con:
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        cur.execute("select distinct genre from "+table)
        return cur.fetchall()

'''
output:
:return a list that contains all of the dates that are in the databse. Because we limited the dates
prior to the program that dates are constants.
'''
def getDates():
    return pd.date_range(start="2018-10-1", end="2019-10-31", freq='D').tolist()

'''
this function creates discretization of energy values. each value can be determined to be 'high' or 'low'
input:
:param energy- values given on scale [0,1]
ouput:
:return the discrite value chosen for the input. if the number is higher than 0.6 then it is high, else it is low.
'''
def getEneryDisc(energy):
    if energy > 0.6:
        return "high"
    else:
        return "low"

'''
this function creates discretization of tempo values. each value can be determined to be 'fast', 'medium or 'slow'
input:
:param tempo- values which are bpm (beats per minute). mostly in range (40-150)
ouput:
:return the discrite value chosen for the input. the discretization conditions are decided after web research about
music bpm count.
'''
def getTempoDisc(tempo):
    if tempo > 120:
        return "fast"
    elif 120 > tempo > 76:
        return "medium"
    else:
        return "slow"

'''
this function is for generating new rows at table with new songs/artists
input:
:param cur- the connection to the database which we use. It should be connected from before
:param row- the row is the object given from the API which will be analyzed
ouput:
:return the function does not return anything but it does insert to the 'songRate' table new values for one of the dates
and if the song is not yet inserted it also added to 'songs' table with all new information.
'''
def rowInsert(cur, row):

    #collecting relevant data for table
    position = row['Position']
    if position==1:
        print(str(row['date']))
    id = row['URL'][31:]
    name = row['Track Name']
    artistName = row['Artist']
    track = sp.track(id)
    artist = track['artists'][0]
    listOfGenres = sp.artist(artist['id'])['genres']

    #handeling unknown genres
    if len(listOfGenres)>0:
        genre =listOfGenres[0]
    else:
        genre ="unknown"

    #collecting audiofeatures (not in the regular API request)
    audioFeatures = sp.audio_features(tracks=[id])
    energy = audioFeatures[0]['energy']
    tempo = audioFeatures[0]['tempo']
    danceability=audioFeatures[0]['danceability']

    #isnert to db
    cur.execute("insert into songs (id, name, artistName, genre, energy, tempo, energyDisc, tempoDisc) select * from (select '" + id + "' as id, ? as name, ? as artistName, '" + genre + "' as genre, " + str(energy) + " as energy, " + str(tempo) + " as tempo, '"+ str(getEneryDisc(energy))+"' as energyDisc, '"+ str(getTempoDisc(tempo))+"' as tempoDisc) as tmp where not exists (select * from songs where id = '" + id + "')",[name,artistName])
    streams = row['Streams']
    rateDate = str(row['date'])
    cur.execute("insert into songRate (id, streams, rateDate, position, region) values (?, ?, ?, ?,?)", [id, streams, rateDate, position, "il"])

'''
after enrating all information from API we do inside calculations of statistics to show the user.
This means how fast/slow are songs and energy flows. We notice that we will go through discretization phase before calculations.
input:
:param cur- the connection to the database which we use. It should be connected from before
:param table- the table we do statistics on (song table so it can be 'songs' or 'normalizedSongs')
:param destTable- a table which is used for keeping all the calculation results.
ouput:
:return the function does not return anything but it does insert to the the destTable the calculated informations
'''
def calculatePercents(cur,table,destTable):
    #creating table
    cur.executescript("drop table if exists "+destTable)
    cur.execute("create table "+destTable+"(genre text, date text, tempoSlowPercent float , tempoMediumPercent float , tempoFastPercent float , energyHighPercent float , energyLowPercent float )")

    #getting axis value that will be input for calculations
    genres = getGenres(table)
    dates = getDates()

    #iterating through each date and genre
    for date in dates:
        for genre in genres:
            sumTempo = str(cur.execute("select sum(tempo) from "+table+" join songRate on "+table+".id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"'").fetchall()[0][0])
            if sumTempo == "None":
                sumTempo = str(1)
            sumEnergy = str(cur.execute("select sum(energy) from "+table+" join songRate on "+table+".id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"'").fetchall()[0][0])
            if sumEnergy == "None":
                sumEnergy = str(1)

            #the actual calculations. we sum all songs and make it into percents.
            cur.execute("insert into "+destTable+" (genre, date, tempoSlowPercent, tempoMediumPercent, tempoFastPercent, energyHighPercent, energyLowPercent) values (?, ?,"+
                        "(select sum(tempo)/"+sumTempo+"*100 from "+table+" join songRate on "+table+".id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and tempoDisc like 'slow')," +
                        "(select sum(tempo)/"+sumTempo+"*100 from "+table+" join songRate on "+table+".id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and tempoDisc like 'medium')," +
                        "(select sum(tempo)/"+sumTempo+"*100 from "+table+" join songRate on "+table+".id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and tempoDisc like 'fast')," +
                        "(select sum(energy)/"+sumEnergy+"*100 from "+table+" join songRate on "+table+".id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and energyDisc like 'high')," +
                        "(select sum(energy)/"+sumEnergy+"*100 from "+table+" join songRate on "+table+".id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and energyDisc like 'low'))", [genre, str(date)])


#start main code. selecting dates, creating tables
# and collecting and saving to db data from APIs.
data = spotifyChartsAPI.get_charts('2018-10-01', '2019-10-31', region='il')
with sqlite3.connect("spotifyGraphDB.sqlite") as con:
    cur = con.cursor()
    cur.executescript("drop table if exists songs")
    cur.execute("create table songs(id text,name text, artistName text, genre text, energy int, tempo int, energyDisc text, tempoDisc text)")
    cur.executescript("drop table if exists songRate")
    cur.execute("create table songRate(id text,streams int, rateDate text,position int,region text)")
    data.apply(lambda row : rowInsert(cur, row), axis=1)
    calculatePercents(cur, "songs", "dailyGenrePercents")
    calculatePercents(cur,"normalizedSongs","normalizedDailyGenrePercents")
