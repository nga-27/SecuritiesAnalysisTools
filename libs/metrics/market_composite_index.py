import pandas as pd 
import numpy as np 

import fix_yahoo_finance as yf 

from libs.tools import cluster_oscs
from libs.utils import generic_plotting

def market_composite_index():
    tickers = 'VGT VHT VCR VDC VFH VDE VIS VOX VNQ VPU VAW'
    data = yf.download(tickers=tickers, period='1y', interval='1d', group_by='ticker')

    ticks = tickers.split(' ')

    composite = []
    for tick in ticks:
        graph, _ = cluster_oscs(data[tick], plot_output=False, function='all')
        composite.append(graph)

    composite2 = []
    for i in range(len(composite[0])):
        s = 0.0
        for j in range(len(composite)):
            s += float(composite[j][i])

        composite2.append(s)

    generic_plotting([composite2])
    return composite2 
