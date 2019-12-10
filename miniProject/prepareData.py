from miniProject import spotifyChartsAPI
import spotipy
import os
import sqlite3
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd


os.environ["SPOTIPY_CLIENT_ID"] = "1b73550cbd9144149ec64aff3a6fc3fc"
os.environ["SPOTIPY_CLIENT_SECRET"] = "aa0fa9dbf7de4ab7b653f15da895c3e3"
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def getGenres():
    with sqlite3.connect("spotifyGraphDB.sqlite") as con:
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        cur.execute("select distinct genre from songs")
        return cur.fetchall()

def getDates():
    return pd.date_range(start="2018-10-1", end="2019-10-31", freq='D').tolist()
    #return pd.date_range(start="2019-10-1", end="2019-10-03", freq='D').tolist()

def getEneryDisc(energy):
    if energy > 0.6:
        return "high"
    else:
        return "low"

def getTempoDisc(tempo):
    if tempo > 120:
        return "fast"
    elif 120 > tempo > 76:
        return "medium"
    else:
        return "slow"


def rowInsert(cur, row):
    position = row['Position']
    if position==1:
        print(str(row['date']))
    id = row['URL'][31:]
    name = row['Track Name']
    artistName = row['Artist']
    track = sp.track(id)
    artist = track['artists'][0]
    listOfGenres=sp.artist(artist['id'])['genres']
    if len(listOfGenres)>0:
        genre =listOfGenres[0]
    else:
        genre ="unknown"
    audioFeatures = sp.audio_features(tracks=[id])
    energy = audioFeatures[0]['energy']
    tempo = audioFeatures[0]['tempo']
    danceability=audioFeatures[0]['danceability']
    cur.execute("insert into songs (id, name, artistName, genre, energy, tempo, energyDisc, tempoDisc) select * from (select '" + id + "' as id, ? as name, ? as artistName, '" + genre + "' as genre, " + str(energy) + " as energy, " + str(tempo) + " as tempo, '"+ str(getEneryDisc(energy))+"' as energyDisc, '"+ str(getTempoDisc(tempo))+"' as tempoDisc) as tmp where not exists (select * from songs where id = '" + id + "')",[name,artistName])
    streams = row['Streams']
    rateDate = str(row['date'])
    cur.execute("insert into songRate (id, streams, rateDate, position, region) values (?, ?, ?, ?,?)", [id, streams, rateDate, position, "il"])

def calculatePercents(cur):
    cur.executescript("drop table if exists dailyGenrePercents")
    cur.execute("create table dailyGenrePercents(genre text, date text, tempoSlowPercent float , tempoMediumPercent float , tempoFastPercent float , energyHighPercent float , energyLowPercent float )")
    genres = getGenres()
    dates = getDates()
    for date in dates:
        for genre in genres:
            sumTempo = str(cur.execute("select sum(tempo) from songs join songRate on songs.id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"'").fetchall()[0][0])
            if sumTempo == "None":
                sumTempo = str(1)
            sumEnergy = str(cur.execute("select sum(energy) from songs join songRate on songs.id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"'").fetchall()[0][0])
            if sumEnergy == "None":
                sumEnergy = str(1)
            cur.execute("insert into dailyGenrePercents (genre, date, tempoSlowPercent, tempoMediumPercent, tempoFastPercent, energyHighPercent, energyLowPercent) values (?, ?,"+
                        "(select sum(tempo)/"+sumTempo+"*100 from songs join songRate on songs.id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and tempoDisc like 'slow')," +
                        "(select sum(tempo)/"+sumTempo+"*100 from songs join songRate on songs.id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and tempoDisc like 'medium')," +
                        "(select sum(tempo)/"+sumTempo+"*100 from songs join songRate on songs.id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and tempoDisc like 'fast')," +
                        "(select sum(energy)/"+sumEnergy+"*100 from songs join songRate on songs.id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and energyDisc like 'high')," +
                        "(select sum(energy)/"+sumEnergy+"*100 from songs join songRate on songs.id = songRate.id where genre like '"+genre+"' and songRate.rateDate = '"+str(date)+"' and energyDisc like 'low'))", [genre, str(date)])


#start main code
data = spotifyChartsAPI.get_charts('2018-10-01', '2019-10-31', region='il')
print(list(data))

with sqlite3.connect("spotifyGraphDB.sqlite") as con:
    cur = con.cursor()
    cur.executescript("drop table if exists songs")
    cur.execute("create table songs(id text,name text, artistName text, genre text, energy int, tempo int, energyDisc text, tempoDisc text)")
    cur.executescript("drop table if exists songRate")
    cur.execute("create table songRate(id text,streams int, rateDate text,position int,region text)")
    data.apply(lambda row : rowInsert(cur, row), axis=1)
    calculatePercents(cur)

# data["Information"] = data.apply(lambda row: sp.track(row['URL']), axis=1)
# print(data)
# print(sp.audio_features(tracks=['1rgnBhdG2JDFTbYkYRZAku']))
# print(sp.track('1rgnBhdG2JDFTbYkYRZAku'))
# print(sp.artist('2NjfBq1NflQcKSeiDooVjY'))
