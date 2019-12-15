import sqlite3
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool, RangeTool, Select
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.io import curdoc
import colorcet as cc
'''


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


def getDates():
    return pd.date_range(start="2018-10-1", end="2019-10-31", freq='D').tolist()


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


def update_plot(attrName, old, new):
    if old == new:
        return
    type = new

    genres = list(getGenres(type))
    palette = [cc.rainbow[i * 15 % cc.rainbow.__len__()] for i in range(genres.__len__())]
    x = getDates()
    if curdoc().get_model_by_name('mainPlot') != None:
        curdoc().clear()

    p = figure(name="mainPlot", y_range=genres, x_axis_type="datetime", x_range=(x[0], x[len(x) - 1]), plot_height=500,
               plot_width=1000, x_axis_label="date", y_axis_label="genres")
    p.add_tools(HoverTool(tooltips=[("low energy", "@energyLowPercent"), ("high energy", "@energyHighPercent"),
                                    ("slow tempo", "@tempoSlowPercent"), ("medium tempo", "@tempoMediumPercent"),
                                    ("fast tempo", "@tempoFastPercent")]))

    for i, genre in enumerate(reversed(genres)):
        y = ridge(genre, getPopularityByGenre(genre, type))
        source = ColumnDataSource(
                data={'x': x, 'y': y, 'energyLowPercent': getTooltipDataForGenre(genre, 'energyLowPercent', type),
                      'energyHighPercent': getTooltipDataForGenre(genre, 'energyHighPercent', type),
                      'tempoSlowPercent': getTooltipDataForGenre(genre, 'tempoSlowPercent', type),
                      'tempoMediumPercent': getTooltipDataForGenre(genre, 'tempoMediumPercent', type),
                      'tempoFastPercent': getTooltipDataForGenre(genre, 'tempoFastPercent', type)})
        p.patch(x='x', y='y', color=palette[i], alpha=0.6, line_color="black", source=source)
        p.scatter(x='x', y='y', color=palette[i], alpha=0.6, line_color="black", source=source, size=2)

    p.outline_line_color = None
    p.background_fill_color = "#efefef"

    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = "#dddddd"
    p.xgrid.ticker = p.xaxis[0].ticker

    p.axis.minor_tick_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.axis_line_color = None

    p.y_range.range_padding = 0.2

    select = figure(title="Drag the middle and edges of the selection box to change the range above",
                    plot_height=130, plot_width=800, y_range=p.y_range,
                    x_axis_type="datetime", y_axis_type=None,
                    tools="", toolbar_location=None, background_fill_color="#efefef", name="rangePlot")

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
update_plot(None, None, 'Normalized')
