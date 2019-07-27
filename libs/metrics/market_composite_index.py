import pandas as pd 
import numpy as np 

import yfinance as yf 

from libs.tools import cluster_oscs
from libs.utils import dual_plotting, ProgressBar, index_appender

def metrics_initializer(period='1y'):
    tickers = 'VGT VHT VCR VDC VFH VDE VIS VOX VNQ VPU VAW'
    sectors = tickers.split(' ')
    tickers = index_appender(tickers)
    print(" ")
    print('Fetching Market Composite Index funds...')
    data = yf.download(tickers=tickers, period=period, interval='1d', group_by='ticker')
    print(" ")
    return data, sectors


def composite_index(data: pd.DataFrame, sectors: list, plot_output=True):
    p = ProgressBar(len(sectors)+2, name='Market Composite Index')
    p.start()

    composite = []
    for tick in sectors:
        graph, _ = cluster_oscs(data[tick], plot_output=False, function='market', wma=False)
        p.uptick()
        composite.append(graph)

    composite2 = []
    for i in range(len(composite[0])):
        s = 0.0
        for j in range(len(composite)):
            s += float(composite[j][i])

        composite2.append(s)
    p.uptick()

    if plot_output:
        dual_plotting(data['^GSPC']['Close'], composite2, y1_label='S&P500', y2_label='MCI', title='Market Composite Index')
    else:
        dual_plotting(data['^GSPC']['Close'], composite2, y1_label='S&P500', y2_label='MCI', title='Market Composite Index', saveFig=True, filename='MCI.png')
    p.uptick()
    return composite2 


def market_composite_index(period='1y'):
    data, sectors = metrics_initializer(period=period)
    composite_index(data, sectors, plot_output=False) 



def type_composite_index(data: pd.DataFrame, sectors: list, plot_output=True):
    p = ProgressBar(13, name='Type Composite Index')
    p.start()

    defensive = []
    cyclical = [] 
    sensitive = []

    composite = {}
    for sect in sectors:
        graph, _ = cluster_oscs(data[sect], plot_output=False, function='market', wma=False)
        p.uptick()
        composite[sect] = graph

    for i in range(len(composite['VGT'])):
        d = float(composite['VHT'][i])
        d += float(composite['VPU'][i])
        d += float(composite['VDC'][i])
        d += float(composite['VNQ'][i]) * 0.25
        defensive.append(d)

        c = float(composite['VNQ'][i]) * 0.75
        c += float(composite['VCR'][i])
        c += float(composite['VFH'][i])
        c += float(composite['VAW'][i])
        cyclical.append(c)

        s = float(composite['VIS'][i])
        s += float(composite['VOX'][i])
        s += float(composite['VDE'][i])
        s += float(composite['VGT'][i])
        sensitive.append(s)

    p.uptick()

