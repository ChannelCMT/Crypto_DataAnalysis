from datetime import datetime, timedelta
import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import talib as ta
import mplfinance as mpf
import sys

class priceChangeData():
    def __init__(self):
        self.author = 'Channel'

    def readDb(self, collection, start, end):
        return pd.DataFrame(
            list(collection.find({"datetime": {'$gt': start, '$lt': end}}))
        )
    
    def resampleDf(self, data, freq='H'):
        dataDf = data.set_index('datetime')
        dataHourDf = dataDf.resample(freq).agg({'open':'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume':'sum'})
        dataResetDf = dataHourDf.reset_index()
        return dataResetDf

    def addSymbol(self, dataDf, symbolName):  
        dataDf['symbol'] = symbolName
        return dataDf

    def setIndex(self, dataDf):
        dataIndex = dataDf.set_index(['datetime', 'symbol'])
        return dataIndex

if __name__ == '__main__':
    getData = priceChangeData()
    startTime = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    endTime = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    symbolList = ['btc_usdt.spot:binance', 'eth_usdt.spot:binance']
    dbClient = pymongo.MongoClient('172.16.20.81', 27017)['Kline_1Min_Auto_Db_Plus']
    columnsName = ['open', 'high', 'low', 'close', 'volume','datetime']
    crytoDict = {
                'btc': getData.readDb(dbClient[symbolList[0]], start=startTime , end=endTime)[columnsName],
                'eth':getData.readDb(dbClient[symbolList[1]], start=startTime , end=endTime)[columnsName]
            }
    multiCryptoDict = {}
    for key, df in crytoDict.items():
        hourDf = getData.resampleDf(df)
        hourSymbolDf = getData.addSymbol(hourDf, key)
        hourIndexDf = getData.setIndex(hourSymbolDf)
        multiCryptoDict[key] = hourIndexDf
    multiDf = pd.concat(list(multiCryptoDict.values())).sort_index()
    # print(multiDf)
    # save the chart
    dataCoin1 = multiDf.loc[:, pd.IndexSlice['btc'], :]
    dataCoin2 = multiDf.loc[:, pd.IndexSlice['eth'], :]
    saveCoin1 = dict(fname='coin1_price.png')
    saveCoin2 = dict(fname='coin2_price.png')
    mpf.plot(dataCoin1.loc[endTime-timedelta(days=31):endTime], type='candle',style='binance', figsize=(20,8), tight_layout=True, savefig=saveCoin1) 
    mpf.plot(dataCoin2.loc[endTime-timedelta(days=31):endTime], type='candle',style='binance', figsize=(20,8), tight_layout=True, savefig=saveCoin2)
    # save the sheet
    def cal_pctChange(data, lastTime, periodList=[1, 2, 3, 4]):
        pctChangeDict = {}
        for period in periodList:
            pctChangeDict['Week'+str(period)] = str(round((data.loc[lastTime-timedelta(hours=(7*(period-1))*24)]/data.loc[lastTime-timedelta(hours=(7*period)*24)]-1)*100, 2))+'%'
        pctChangeDict['monthly'] = str(round((data.loc[lastTime]/data.loc[lastTime-timedelta(hours=(7*4)*24)]-1)*100, 2))+'%'
        pctChangeDf = pd.Series(pctChangeDict)
        return pctChangeDf
    lastTime = dataCoin1.index[-1]
    pctCoin1 = cal_pctChange(dataCoin1.close, lastTime)
    pctCoin2 = cal_pctChange(dataCoin2.close, lastTime)
    pctChangeDf = pd.DataFrame({
    'btc_pctChange': cal_pctChange(dataCoin1.close, lastTime),
    'eth_pctChange': cal_pctChange(dataCoin2.close, lastTime)
    })
    pctChangeDfT = pctChangeDf.T
    pctChangeDfT.to_excel('PricePctChange.xlsx')
