import sqlite3
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool, RangeTool, Select
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.io import curdoc
import colorcet as cc
'''
this class is the main execution class. its purpose is to collect the wanted data from the 
database and to insert it to a the dynamic graphs that are seen when running this class as 
a bokeh server.
'''


'''
input:
:param type-can be either "full" or "normalized". full means that we get all of the 
genres and normalized are the genres we created that merge small genres into main genres.
output:
:return a list of genre names (as written in the database)
'''
def getGenres(type):
    with sqlite3.connect("spotifyGraphDB.sqlite") as con:
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        table = 'songs'
        if type == 'Normalized':
            table = 'NormalizedSongs'
        cur.execute("select distinct genre from " + table)
        return cur.fetchall()


'''
output:
:return a list that contains all of the dates that are in the databse. Because we limited the dates
prior to the program that dates are constants.
'''
def getDates():
    return pd.date_range(start="2018-10-1", end="2019-10-31", freq='D').tolist()

'''
input:
:param type-can be either "full" or "normalized". if the type is full then we need to fetch data from the table 'songs'
and not the table 'normalizedSongs' which has the normalized data.
:param genre- the genre in the database where we want the data from (should be normalized genre or not depends on the type)
output:
:return a list of numbers. each number is a popularity rank made out of the measurement we created for one day. It ordered so 
the first number is for the 1/10/18 and the last number is the genre popularity for 31/10/19.
The rank is a meseaurment for popularity. Because we look the the 30 most popular songs everyday so we have rankings 
from 1 to 30. because rank 1 is more valuable than rank 30 so we needed to invert the values and also to 
make it between [0,1]. The final meseaurement is average(ranksOfGenreSongs) where rankOfGenreSongs = (30-song.rate/30| song in genre) 
'''
def getPopularityByGenre(genre, type):
    with sqlite3.connect("spotifyGraphDB.sqlite") as con:
        table = 'songs'
        if type == 'Normalized':
            table = 'NormalizedSongs'
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        cur.execute(
            "select COALESCE(avg, 0) as avg from (select distinct songRate.rateDate from songRate) as dates left join (select (30- Avg(position))/31 as avg, rateDate from (select id from " + table + " where genre like '" + genre + "') as ids join songRate on ids.id = songRate.id group by rateDate order by rateDate) as actualResult on dates.rateDate = actualResult.rateDate")
        return cur.fetchall()

'''
input:
:param type - can be either "full" or "normalized". if the type is full then we need to fetch data from the table 'DailyGenrePercents'
and not the table 'normalizedDailyGenrePercents' that has different calculations
:param genre- the genre in the database where we want the data from (should be normalized genre or not depends on the type)
:param title- that is the title of each number. if we look for 'energyLowPercent' that would be the title
output:
:return a list of numbers. It ordered so 
the first number is for the 1/10/18 and the last number is the genre popularity for 31/10/19.
The number is the percents of this title in this genre for everyday in the time interval.
'''
def getTooltipDataForGenre(genre, title, type):
    with sqlite3.connect("spotifyGraphDB.sqlite") as con:
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        table = 'DailyGenrePercents'
        if type == 'Normalized':
            table = 'normalizedDailyGenrePercents'
        cur.execute("select " + title + " from " + table + " where genre = '" + genre + "'")

        def fixZeros(x):
            if x == None:
                return 0
            else:
                return x

        return list(map(lambda x: fixZeros(x), list(cur.fetchall())))
'''
input:
:param type-can be either "full" or "normalized". if the type is full then we need to fetch data from the table 'songs'
and not the table 'normalizedSongs' which has the normalized data.
:param genre- the genre in the database where we want the data from (should be normalized genre or not depends on the type)
output:
:return a list of tuples. each tuple contains the genre inserted and its popularity for one day. It ordered so 
the first tuple is for the 1/10/18 and the last tuple is the genre popularity for 31/10/19.
note that this is the format needed for the graph. Note that we zeroed out the first and last days and that is because
it makes the graphs more readable and intuitive for graphical reasons.
'''
def ridge(category, data, scale=1):
    data = list(zip([category] * len(data), scale * data))

    # replace last value with value 0. for graphic reasons
    data.pop(len(data) - 1)
    data.append((category, 0))
    data.append((category, 0))

    # replace first value with value 0. for graphic reasons
    data.pop(0)
    data.insert(0, (category, 0))
    return data

'''
this function creates the graph. Because it is also an event function it should follow the onChange function interface
and have 3 attributes. The first time it is called manually and other times it is called from the combo box in the GUI.
input:
:param attrName- when clicked the attribute that called the function is inserted here
:param old- when the combo box changes the value before the search goes here
:param new- when the combo box changes the value chosen after the search goes here
output:
:return it has no function output but it does change the GUI from normalized to full genres or the other way around.
'''
def update_plot(attrName, old, new):
    if old == new:
        return
    type = new
    #getting axis values
    genres = list(getGenres(type))
    palette = [cc.rainbow[i * 15 % cc.rainbow.__len__()] for i in range(genres.__len__())]
    x = getDates()

    #cleaning the website if already has stuff on it
    if curdoc().get_model_by_name('mainPlot') != None:
        curdoc().clear()

    #creating main graph
    p = figure(name="mainPlot", y_range=genres, x_axis_type="datetime", x_range=(x[0], x[len(x) - 1]), plot_height=500,
               plot_width=1000, x_axis_label="date", y_axis_label="genres")

    #creating tooltip structure
    p.add_tools(HoverTool(tooltips=[("low energy", "@energyLowPercent"), ("high energy", "@energyHighPercent"),
                                    ("slow tempo", "@tempoSlowPercent"), ("medium tempo", "@tempoMediumPercent"),
                                    ("fast tempo", "@tempoFastPercent")]))

    #iterating through genres and adding subgraphs
    for i, genre in enumerate(reversed(genres)):
        y = ridge(genre, getPopularityByGenre(genre, type))
        source = ColumnDataSource(
                data={'x': x, 'y': y, 'energyLowPercent': getTooltipDataForGenre(genre, 'energyLowPercent', type),
                      'energyHighPercent': getTooltipDataForGenre(genre, 'energyHighPercent', type),
                      'tempoSlowPercent': getTooltipDataForGenre(genre, 'tempoSlowPercent', type),
                      'tempoMediumPercent': getTooltipDataForGenre(genre, 'tempoMediumPercent', type),
                      'tempoFastPercent': getTooltipDataForGenre(genre, 'tempoFastPercent', type)})


        #load subgraphs
        p.patch(x='x', y='y', color=palette[i], alpha=0.6, line_color="black", source=source)

        #load the tooltips
        p.scatter(x='x', y='y', color=palette[i], alpha=0.6, line_color="black", source=source, size=2)


    #graphic configurations
    p.outline_line_color = None
    p.background_fill_color = "#efefef"
    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = "#dddddd"
    p.xgrid.ticker = p.xaxis[0].ticker
    p.axis.minor_tick_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.axis_line_color = None
    p.y_range.range_padding = 0.2

    #date range bar at the bottom is initanalized here
    select = figure(title="Drag the middle and edges of the selection box to change the range above",
                    plot_height=130, plot_width=800, y_range=p.y_range,
                    x_axis_type="datetime", y_axis_type=None,
                    tools="", toolbar_location=None, background_fill_color="#efefef", name="rangePlot")

    #date range bar configurations
    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2
    select.line('x', 'y', source=source)
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool

    # add option bar for full, normalzed and add to row
    distribution_select = Select(value=type, title='Genres Viewed', options=['Full', 'Normalized'], name="selectType")
    distribution_select.on_change('value', update_plot)

    curdoc().add_root(column(distribution_select, p, select, name="mainLayout"))


###########################################Main
'''
We first run this manually and it will automatically build on our server the graphs and from now on 
all the changes will be using the combo box
'''
update_plot(None, None, 'Normalized')
