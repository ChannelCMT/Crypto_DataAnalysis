from datetime import datetime, timedelta

startTime = datetime(2023,2,5,8)
endTime = datetime(2023,2,13,9)

import warnings
warnings.filterwarnings("ignore")

import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import talib as ta

symbolList = ['btc_usdt.spot:binance', 'eth_usdt.spot:binance']

client = pymongo.MongoClient('172.16.20.81', 27017)

def readDb(collection, start, end):
    return pd.DataFrame(
        list(collection.find({"datetime": {'$gt': start, '$lt': end}}))
    )

dbClient = client['Kline_1Min_Auto_Db_Plus']
columnsName = ['open', 'high', 'low', 'close', 'volume','datetime']
crytoDict = {
                'btc':readDb(dbClient[symbolList[0]], start=startTime , end=endTime)[columnsName],
                'eth':readDb(dbClient[symbolList[1]], start=startTime , end=endTime)[columnsName]
            }

def resampleDf(data, freq='H'):
#     df = data.drop('_id', axis=1)
    dataDf = data.set_index('datetime')
    dataHourDf = dataDf.resample(freq).agg({'open':'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume':'sum'})
    dataResetDf = dataHourDf.reset_index()
    return dataResetDf

def addSymbol(dataDf, symbolName):  
    dataDf['symbol'] = symbolName
    return dataDf

def setIndex(dataDf):
    dataIndex = dataDf.set_index(['datetime', 'symbol'])
    return dataIndex

multiCryptoDict = {}
for key, df in crytoDict.items():
    hourDf = resampleDf(df)
    hourSymbolDf = addSymbol(hourDf, key)
    hourIndexDf = setIndex(hourSymbolDf)
    multiCryptoDict[key] = hourIndexDf

multiDf = pd.concat(list(multiCryptoDict.values())).sort_index()

dataCoin1 = multiDf.loc[:, pd.IndexSlice['btc'], :]
dataCoin2 = multiDf.loc[:, pd.IndexSlice['eth'], :]

def cal_pctChange(data, lastTime, periodList=[1, 3, 5, 7]):
    pctChangeDict = {}
    for period in periodList:
        pctChangeDict[str(period)+'Day'] = str(round((data.loc[lastTime]/data.loc[lastTime-timedelta(hours=period*24)]-1)*100, 2))+'%'
    pctChangeDf = pd.Series(pctChangeDict)
    return pctChangeDf

lastTime = dataCoin1.index[-1]
pctCoin1 = cal_pctChange(dataCoin1.close, lastTime)
pctCoin2 = cal_pctChange(dataCoin2.close, lastTime)
pctChangeDf = pd.DataFrame({
    'btc_pctChange': cal_pctChange(dataCoin1.close, lastTime),
    'eth_pctChange': cal_pctChange(dataCoin2.close, lastTime),
})

pctChangeDfT = pctChangeDf.T

pctChangeDfT.to_excel('PricePctChange.xlsx')

from bokeh.models import BoxAnnotation
from bokeh.models import ColumnDataSource, Label, LabelSet, Range1d, Arrow, OpenHead
from bokeh.layouts import column
from math import pi
from bokeh.plotting import figure
from bokeh.io import output_notebook,show, save
from bokeh.resources import INLINE
import bokeh.io
from bokeh import *
bokeh.io.output_notebook(INLINE)

inc = dataCoin1.close > dataCoin1.open
dec = dataCoin1.open > dataCoin1.close

w = 12*60*60*50

## Candlestick chart
candlestick = figure(x_axis_type="datetime", plot_width=800, plot_height=500, title = "BTC", toolbar_location=None)

candlestick.segment(dataCoin1.index[inc], dataCoin1.high[inc], dataCoin1.index[inc], dataCoin1.low[inc], color="green")
candlestick.segment(dataCoin1.index[dec], dataCoin1.high[dec], dataCoin1.index[dec], dataCoin1.low[dec], color="red")

candlestick.vbar(dataCoin1.index[inc], w, dataCoin1.open[inc], dataCoin1.close[inc],
         fill_color="green", line_color="green")

candlestick.vbar(dataCoin1.index[dec], w, dataCoin1.open[dec], dataCoin1.close[dec],
         fill_color="red", line_color="red")

Now = dataCoin1.index[-1]
x1Days = dataCoin1.index[-1]-timedelta(days=1)
x3Days = dataCoin1.index[-1]-timedelta(days=3)
x5Days = dataCoin1.index[-1]-timedelta(days=5)
x7Days = dataCoin1.index[-1]-timedelta(days=7)


candlestick.add_layout(Arrow(x_start=x1Days, x_end=Now, y_start=dataCoin1.close[x1Days], y_end=dataCoin1.close[Now],
                     end=OpenHead(line_color="orange", line_width=2, line_alpha=1),
                     line_color="orange", line_width=2, line_alpha=1, line_dash='dashed'
                    ))
citation1 = Label(x=x1Days, y=dataCoin1.close[x1Days], x_units='data', y_units='data',
                 text=pctChangeDfT.loc['btc_pctChange']['1Day'], render_mode='css',
                 border_line_color='orange', border_line_alpha=1.0,
                 background_fill_color='orange', background_fill_alpha=1.0,
                 text_color="white")

candlestick.add_layout(Arrow(x_start=x3Days, x_end=Now, y_start=dataCoin1.close[x3Days], y_end=dataCoin1.close[Now],
                     end=OpenHead(line_color="olive", line_width=2, line_alpha=1),
                     line_color="olive", line_width=2, line_alpha=1, line_dash='dashed'
                    ))

citation3 = Label(x=x3Days, y=dataCoin1.close[x3Days], x_units='data', y_units='data',
                 text=pctChangeDfT.loc['btc_pctChange']['3Day'], render_mode='css',
                 border_line_color='olive', border_line_alpha=1.0,
                 background_fill_color='olive', background_fill_alpha=1.0,
                 text_color="white")

candlestick.add_layout(Arrow(x_start=x5Days, x_end=Now, y_start=dataCoin1.close[x5Days], y_end=dataCoin1.close[Now],
                     end=OpenHead(line_color="lime", line_width=2, line_alpha=1),
                     line_color="lime", line_width=2, line_alpha=1, line_dash='dashed'
                    ))

citation5 = Label(x=x5Days, y=dataCoin1.close[x5Days], x_units='data', y_units='data',
                 text=pctChangeDfT.loc['btc_pctChange']['5Day'], render_mode='css',
                 border_line_color='lime', border_line_alpha=1.0,
                 background_fill_color='lime', background_fill_alpha=1.0,
                 text_color="white")

candlestick.add_layout(Arrow(x_start=x7Days, x_end=Now, y_start=dataCoin1.close[x7Days], y_end=dataCoin1.close[Now],
                     end=OpenHead(line_color="cyan", line_width=2, line_alpha=1),
                     line_color="cyan", line_width=2, line_alpha=1, line_dash='dashed'
                    ))

citation7 = Label(x=x7Days, y=dataCoin1.close[x7Days], x_units='data', y_units='data',
                 text=pctChangeDfT.loc['btc_pctChange']['7Day'], render_mode='css',
                 border_line_color='cyan', border_line_alpha=1.0,
                 background_fill_color='cyan', background_fill_alpha=1.0,
                 text_color="white")

candlestick.add_layout(citation1)
candlestick.add_layout(citation3)
candlestick.add_layout(citation5)
candlestick.add_layout(citation7)
show(candlestick)
bokeh.io.export_png(candlestick , filename="./coin1_price.png")
# save(candlestick, "coin1_price.png")