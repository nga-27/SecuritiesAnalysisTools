import pandas as pd 
import numpy as np 
from datetime import datetime

from libs.utils import download_data_indexes, index_appender, ProgressBar
from libs.utils import dual_plotting
from libs.tools import beta_comparison_list

def correlation_composite_index(config: dict, plot_output=True):
    corr = dict()
    if config.get('properties', {}).get('Indexes', {}).get('Correlation', {}).get('run', False):
        config['duration'] = config.get('properties', {}).get('Indexes', {}).get('Correlation', {}).get('type', 'long')
        data, sectors = metrics_initializer(config['duration'])
        corr = get_correlation(data, sectors, plot_output=plot_output)
    return corr


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


def get_correlation(data: dict, sectors: list, plot_output=True) -> dict:
    PERIOD_LENGTH = [100, 50, 25]
    corr_data = dict()

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

        norm_corr = []
        for nc_period in net_correlation:
            max_ = np.max(nc_period)
            norm = [x / max_ for x in nc_period]
            norm_corr.append(norm)
        net_correlation = norm_corr.copy()

        dual_plotting(  net_correlation, 
                        data['^GSPC']['Close'][start_pt:tot_len], 
                        x=dates,
                        y1_label=legend, 
                        y2_label='S&P500', 
                        title='CCI Net Correlation', 
                        saveFig=(not plot_output), 
                        filename='CCI_net_correlation.png')

        str_dates = []
        for date in dates:
            str_dates.append(date.strftime("%Y-%m-%d"))
        
        for i, nc_period in enumerate(net_correlation):
            corr_data[legend[i]] = {}
            corr_data[legend[i]]['data'] = nc_period.copy()
            corr_data[legend[i]]['date'] = str_dates.copy()
        progress_bar.end()

    return corr_data
