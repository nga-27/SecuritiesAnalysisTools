import pandas as pd 
import numpy as np 
from datetime import datetime

from libs.utils import download_data_indexes, index_appender, ProgressBar
from libs.utils import dual_plotting
from libs.tools import beta_comparison_list

def correlation_composite_index(config: dict, plot_output=True):
    data, sectors = metrics_initializer(config['duration'])
    get_correlation(data, sectors, plot_output=plot_output)


def metrics_initializer(duration: str='long') -> list:
    tickers = 'VGT VHT VCR VDC VFH VDE VIS VOX VNQ VPU VAW'
    START = '2005-01-01'
    sectors = tickers.split(' ')
    tickers = index_appender(tickers)
    all_tickers = tickers.split(' ')
    date = datetime.now().strftime('%Y-%m-%d')
    print(" ")
    print('Fetching Correlation Composite Index funds...')
    if duration == 'short':
        data, _ = download_data_indexes(indexes=all_tickers, tickers=tickers, period='2y', interval='1d')
    else:
        data, _ = download_data_indexes(indexes=all_tickers, tickers=tickers, start=START, end=date, interval='1d')
    print(" ")
    return data, sectors

def get_correlation(data: dict, sectors: list, plot_output=True):
    PERIOD_LENGTH = [100, 50, 25]
    if '^GSPC' in data.keys():
        tot_len = len(data['^GSPC']['Close'])
        start_pt = max(PERIOD_LENGTH)
        ups = int(np.ceil((tot_len-start_pt)/250.0))

        progress_bar = ProgressBar(11*ups*len(PERIOD_LENGTH) + 1, name="Correlation Composite Index")
        progress_bar.start()

        corrs = {}
        dates = data['^GSPC'].index[start_pt:tot_len]
        net_correlation = []
        legend = []
        for period in PERIOD_LENGTH:
            nc = [0.0] * (tot_len-start_pt)
            for sector in sectors:
                corrs[sector] = []
                counter = 0
                for i in range(start_pt, tot_len):
                    _, rsqd = beta_comparison_list(data[sector]['Close'][i-period:i], data['^GSPC']['Close'][i-period:i])
                    corrs[sector].append(rsqd)
                    nc[i-start_pt] += rsqd
                    counter += 1
                    if counter == 250:
                        progress_bar.uptick()
                        counter = 0
            net_correlation.append(nc.copy())
            legend.append('Corr-' + str(period))

        dual_plotting(  net_correlation, 
                        data['^GSPC']['Close'][start_pt:tot_len], 
                        x=dates,
                        y1_label=legend, 
                        y2_label='S&P500', 
                        title='CCI Net Correlation', 
                        saveFig=(not plot_output), 
                        filename='CCI_net_correlation.png')
        
        progress_bar.end()
