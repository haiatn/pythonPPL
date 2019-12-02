import spotifyChartsAPI
import spotipy
import os
import sqlite3
from spotipy.oauth2 import SpotifyClientCredentials


os.environ["SPOTIPY_CLIENT_ID"] = "1b73550cbd9144149ec64aff3a6fc3fc"
os.environ["SPOTIPY_CLIENT_SECRET"] = "aa0fa9dbf7de4ab7b653f15da895c3e3"
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)




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
    audioFeatures = sp.audio_features(tracks=['id'])
    energy = audioFeatures[0]['energy']
    tempo = audioFeatures[0]['tempo']
    danceability=audioFeatures[0]['danceability']
    cur.execute("insert into songs (id, name, artistName, genre, energy, tempo, danceability) select * from (select '" + id + "' as id, ? as name, ? as artistName, '" + genre + "' as genre, " + str(energy) + " as energy, " + str(tempo) + " as tempo, "+ str(danceability)+" as danceability) as tmp where not exists (select * from songs where id = '" + id + "')",[name,artistName])
    streams = row['Streams']
    rateDate = str(row['date'])
    cur.execute("insert into songRate (id, streams, rateDate, position, region) values (?, ?, ?, ?,?)", [id, streams, rateDate, position, "il"])


#start main code
data = spotifyChartsAPI.get_charts('2019-10-01', '2019-10-31', region='il')
print(list(data))

with sqlite3.connect("spotifyGraphDB.sqlite") as con:
    cur = con.cursor()
    #cur.executescript("drop table if exists songs")
    #cur.execute("create table songs(id text,name text, artistName text, genre text, energy int, tempo int,danceability int)")
    #cur.executescript("drop table if exists songRate")
    #cur.execute("create table songRate(id text,streams int, rateDate text,position int,region text)")
    data.apply(lambda row : rowInsert(cur, row), axis=1)

# data["Information"] = data.apply(lambda row: sp.track(row['URL']), axis=1)
# print(data)
# print(sp.audio_features(tracks=['1rgnBhdG2JDFTbYkYRZAku']))
# print(sp.track('1rgnBhdG2JDFTbYkYRZAku'))
# print(sp.artist('2NjfBq1NflQcKSeiDooVjY'))
