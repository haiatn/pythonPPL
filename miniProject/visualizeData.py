import sqlite3
import pandas as pd
from numpy import linspace
from scipy.stats.kde import gaussian_kde

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, FixedTicker, PrintfTickFormatter, HoverTool
from bokeh.plotting import figure
from bokeh.sampledata.perceptions import probly

import colorcet as cc

def getGenres():
    with sqlite3.connect("spotifyGraphDB.sqlite") as con:
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        cur.execute("select distinct genre from songs")
        return cur.fetchall()

def getPopularityByGenre(genre):
    with sqlite3.connect("spotifyGraphDB.sqlite") as con:
        con.row_factory=lambda cursor, row: row[0]
        cur = con.cursor()
        cur.execute("select COALESCE(avg, 0) as avg from (select distinct songRate.rateDate from songRate) as dates left join (select (30- Avg(position))/31 as avg, rateDate from (select id from songs where genre like '"+genre+"') as ids join songRate on ids.id = songRate.id group by rateDate order by rateDate) as actualResult on dates.rateDate = actualResult.rateDate")
        return cur.fetchall()

def getDates():
    return pd.date_range(start="2018-10-1", end="2019-10-31", freq='D').tolist()

def getTooltipData(genre, date):
    with sqlite3.connect("spotifyGraphDB.sqlite") as con:
        con.row_factory=lambda cursor, row: row[0]
        cur = con.cursor()
        cur.execute("select * from dailyGenrePercents where genre = '"+genre+"' and date = '"+str(date)+"'")
        return cur.fetchall()

output_file("spotifyGraph.html")

def ridge(category, data, scale=1):
    data=list(zip([category]*len(data), scale*data))
    #replace last value with value 0. for graphic reasons
    data.pop(len(data)-1)
    data.append((category,0))
    # replace first value with value 0. for graphic reasons
    data.pop(0)
    data.insert(0,(category,0))

    return data

genres = list(getGenres())
palette = [cc.rainbow[i*15 % cc.rainbow.__len__()] for i in range(genres.__len__())]
x = getDates()

p = figure(y_range=genres, x_axis_type="datetime",plot_width=1300, x_axis_label="date", y_axis_label = "genres")

for i, genre in enumerate(reversed(genres)):
    y = ridge(genre, getPopularityByGenre(genre))
    source = ColumnDataSource(data={'x': x, 'y': y})
    p.patch(x='x', y='y', color=palette[i], alpha=0.6, line_color="black", source=source)
    p.add_tools(HoverTool(tooltips=[("slow tempo", "@tempoSlowPercent"), ("medium tempo", "@tempoMediumPercent"), ("fast tempo", "@tempoFactPercent")]))
    # p.add_tools(HoverTool(tooltips=[("low energy", "@energyLowPercent"), ("high energy", "@energyHighPercent")]))

p.outline_line_color = None
p.background_fill_color = "#efefef"

p.ygrid.grid_line_color = None
p.xgrid.grid_line_color = "#dddddd"
p.xgrid.ticker = p.xaxis[0].ticker

p.axis.minor_tick_line_color = None
p.axis.major_tick_line_color = None
p.axis.axis_line_color = None

p.y_range.range_padding = 0.2

show(p)

'''
sql for normalizing
UPDATE normalizedGenresSongs
SET genre="hip hop and rap"
WHERE
    genre Like '%rap%' or genre like '%hip%' or genre like '%r&b%';
UPDATE normalizedGenresSongs
SET genre="israeli"
WHERE
    genre Like '%israel%' or genre Like '%unknown%';
	UPDATE normalizedGenresSongs
SET genre="rock"
WHERE
    genre Like '%rock%';
UPDATE normalizedGenresSongs
SET genre="pop"
WHERE
    genre Like '%pop%' or genre Like '%dance%' or genre="boy band";	
	UPDATE normalizedGenresSongs
SET genre="electronic"
WHERE
    genre= "big room" or genre='edm' or genre='brostep';	

'''