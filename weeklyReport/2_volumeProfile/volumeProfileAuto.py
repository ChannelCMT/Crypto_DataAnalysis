from datetime import datetime, timedelta
import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import talib as ta
import numpy as np
import mplfinance as mpf
import sys
from scipy import stats, signal

# python volumeProfileAuto.py '2023-01-01' '2023-01-31'

class volumeProfileData():
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

    def cal_resistance_surport(self, dataPv):
        kde_factor = 0.05
        num_samples = 500
        kde = stats.gaussian_kde(dataPv.close.values,weights=dataPv.volume.values, bw_method=kde_factor)
        xr = np.linspace(dataPv.close.min(),dataPv.close.max(),num_samples)
        kdy = kde(xr)
        ticks_per_sample = (xr.max() - xr.min()) / num_samples
        min_prom = kdy.max() * 0.8
        width_range= 1
        peaks, peak_props = signal.find_peaks(kdy, prominence=min_prom, width=width_range, rel_height=0.75)
        left_ips = peak_props['left_ips']
        right_ips = peak_props['right_ips']
        pkx = xr[peaks]
        pky = kdy[peaks]
        width_x0 = xr.min() + (left_ips * ticks_per_sample)
        width_x1 = xr.min() + (right_ips * ticks_per_sample)
        return round(pkx[0], 2), round(width_x0[0], 2), round(width_x1[0], 2)


if __name__ == '__main__':
    getData = volumeProfileData()
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
        hourDf = getData.resampleDf(df, '15Min')
        hourSymbolDf = getData.addSymbol(hourDf, key)
        hourIndexDf = getData.setIndex(hourSymbolDf)
        multiCryptoDict[key] = hourIndexDf
    multiDf = pd.concat(list(multiCryptoDict.values())).sort_index()
    # print(multiDf)
    # save the chart
    dataCoin1 = multiDf.loc[:, pd.IndexSlice['btc'], :]
    dataCoin2 = multiDf.loc[:, pd.IndexSlice['eth'], :]
    data1Pv = dataCoin1[['close', 'volume']]
    data2Pv = dataCoin2[['close', 'volume']]
    dataBtcPvDf = dataCoin1.set_index('close').sort_index()
    dataEthPvDf = dataCoin2.set_index('close').sort_index()

    week15Min = 672
    pocBtc4, SupportBtc4, ResistanceBtc4 = getData.cal_resistance_surport(data1Pv.iloc[-week15Min:])
    pocBtc3, SupportBtc3, ResistanceBtc3 = getData.cal_resistance_surport(data1Pv.iloc[-week15Min*2:-week15Min])
    pocBtc2, SupportBtc2, ResistanceBtc2 = getData.cal_resistance_surport(data1Pv.iloc[-week15Min*3:-week15Min*2])
    pocBtc1, SupportBtc1, ResistanceBtc1 = getData.cal_resistance_surport(data1Pv.iloc[-week15Min*4:-week15Min*3])

    pocEth4, SupportEth4, ResistanceEth4 = getData.cal_resistance_surport(data2Pv.iloc[-week15Min:])
    pocEth3, SupportEth3, ResistanceEth3 = getData.cal_resistance_surport(data2Pv.iloc[-week15Min*2:-week15Min])
    pocEth2, SupportEth2, ResistanceEth2 = getData.cal_resistance_surport(data2Pv.iloc[-week15Min*3:-week15Min*2])
    pocEth1, SupportEth1, ResistanceEth1 = getData.cal_resistance_surport(data2Pv.iloc[-week15Min*4:-week15Min*3])
    
    btcVolumeProfile = pd.DataFrame({'btcVolumeProfile': ('Point Of Control', 'Support', 'Resistance'),
    'week4_btc': (pocBtc4, SupportBtc4, ResistanceBtc4),
    'week3_btc': (pocBtc3, SupportBtc3, ResistanceBtc3),
    'week2_btc': (pocBtc2, SupportBtc2, ResistanceBtc2),
    'week1_btc': (pocBtc1, SupportBtc1, ResistanceBtc1)
    })

    ethVolumeProfile = pd.DataFrame({'ethVolumeProfile': ('Point Of Control', 'Support', 'Resistance'),
    'week4_eth': (pocEth4, SupportEth4, ResistanceEth4),
    'week3_eth': (pocEth3, SupportEth3, ResistanceEth3),
    'week2_eth': (pocEth2, SupportEth2, ResistanceEth2),
    'week1_eth': (pocEth1, SupportEth1, ResistanceEth1)
    })

    btcVolumeProfileDf = btcVolumeProfile.set_index('btcVolumeProfile').T
    ethVolumeProfileDf = ethVolumeProfile.set_index('ethVolumeProfile').T
    btcVolumeProfileDf.to_excel('btcVolumeProfileDf.xlsx')
    ethVolumeProfileDf.to_excel('ethVolumeProfileDf.xlsx')

    dataBtcDay = getData.resampleDf(getData.readDb(dbClient[symbolList[0]], start=startTime , end=endTime)[columnsName], 'D')
    dataEthDay = getData.resampleDf(getData.readDb(dbClient[symbolList[1]], start=startTime , end=endTime)[columnsName], 'D')

    fBtc, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(18,7))
    ax1.set_title('Monthly_volumeProfile')
    ax1.plot(dataBtcDay.close)
    ax1.hlines(pocBtc4, dataBtcDay.index[0], dataBtcDay.index[-1] , linestyles='dashed', alpha=0.7, color='red', label='POC_Week4')
    ax1.hlines(pocBtc3, dataBtcDay.index[0], dataBtcDay.index[-1] , linestyles='dashed', alpha=0.7, color='orange', label='POC_Week3')
    ax1.hlines(pocBtc2, dataBtcDay.index[0], dataBtcDay.index[-1] , linestyles='dashed', alpha=0.7, color='yellow', label='POC_Week2')
    ax1.hlines(pocBtc1, dataBtcDay.index[0], dataBtcDay.index[-1] , linestyles='dashed', alpha=0.7, color='g', label='POC_Week1')
    ax1.legend()
    ax1.set_title('Monthly_btcPrice')
    ax1.grid()
    for tick in ax1.get_xticklabels():
        tick.set_rotation(30)
    ax2.barh(data1Pv.close.iloc[-week15Min:], data1Pv.volume.iloc[-week15Min:], height=50, color='red', label='Week4')
    ax2.barh(data1Pv.close.iloc[-week15Min*2:-week15Min], data1Pv.volume.iloc[-week15Min*2:-week15Min], height=50, color='orange', label='Week3')
    ax2.barh(data1Pv.close.iloc[-week15Min*3:-week15Min*2], data1Pv.volume.iloc[-week15Min*3:-week15Min*2], height=50, color='yellow', label='Week2')
    ax2.barh(data1Pv.close.iloc[-week15Min*4:-week15Min*3], data1Pv.volume.iloc[-week15Min*4:-week15Min*3], height=50, color='g', label='Week1')
    ax2.grid()
    ax2.invert_xaxis()
    ax2.legend()
    fBtc.savefig('btcVolumeProfile')

    fEth, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(18,7))
    ax1.set_title('Monthly_volumeProfile')
    ax1.plot(dataEthDay.close)
    ax1.hlines(pocEth4, dataEthDay.index[0], dataEthDay.index[-1] , linestyles='dashed', alpha=0.7, color='red', label='POC_Week4')
    ax1.hlines(pocEth3, dataEthDay.index[0], dataEthDay.index[-1] , linestyles='dashed', alpha=0.7, color='orange', label='POC_Week3')
    ax1.hlines(pocEth2, dataEthDay.index[0], dataEthDay.index[-1] , linestyles='dashed', alpha=0.7, color='yellow', label='POC_Week2')
    ax1.hlines(pocEth1, dataEthDay.index[0], dataEthDay.index[-1] , linestyles='dashed', alpha=0.7, color='g', label='POC_Week1')
    ax1.legend()
    ax1.set_title('Monthly_ethPrice')
    ax1.grid()
    for tick in ax1.get_xticklabels():
        tick.set_rotation(30)
    ax2.barh(data2Pv.close.iloc[-week15Min:], data2Pv.volume.iloc[-week15Min:], height=10, color='red', label='Week4')
    ax2.barh(data2Pv.close.iloc[-week15Min*2:-week15Min], data2Pv.volume.iloc[-week15Min*2:-week15Min], height=10, color='orange', label='Week3')
    ax2.barh(data2Pv.close.iloc[-week15Min*3:-week15Min*2], data2Pv.volume.iloc[-week15Min*3:-week15Min*2], height=10, color='yellow', label='Week2')
    ax2.barh(data2Pv.close.iloc[-week15Min*4:-week15Min*3], data2Pv.volume.iloc[-week15Min*4:-week15Min*3], height=10, color='g', label='Week1')
    ax2.grid()
    ax2.invert_xaxis()
    ax2.legend()
    fEth.savefig('ethVolumeProfile')