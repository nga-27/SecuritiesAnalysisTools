import pandas as pd 
import numpy as np 

import fix_yahoo_finance as yf 

from libs.tools import cluster_oscs
from libs.utils import dual_plotting, ProgressBar, index_appender

def market_composite_index(plot_output=True):
    tickers = 'VGT VHT VCR VDC VFH VDE VIS VOX VNQ VPU VAW'
    ticks = tickers.split(' ')
    p = ProgressBar(13, name='Market Composite Index')
    tickers = index_appender(tickers)
    data = yf.download(tickers=tickers, period='1y', interval='1d', group_by='ticker')
    p.start()

    composite = []
    for tick in ticks:
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
