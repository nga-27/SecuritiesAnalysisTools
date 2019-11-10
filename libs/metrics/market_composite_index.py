"""
market_composite_index.py

An equal-weight aggregate metric that takes the computed clustered oscillator metric 
for each of the 11 sectors of the market represented by the Vanguard ETFs listed under
'tickers' below in 'metrics_initializer'. Arguably a more accurate metric than a 
clustered oscillator metric on the S&P500 by itself. 

FUTURE - compare this metric with a correlation metric of each sector.
"""

import pandas as pd 
import numpy as np 

import yfinance as yf 

from libs.tools import cluster_oscs, beta_comparison_list
from libs.utils import dual_plotting, generic_plotting
from libs.utils import ProgressBar, index_appender
from libs.utils import download_data_indexes

def metrics_initializer(period='1y'):
    tickers = 'VGT VHT VCR VDC VFH VDE VIS VOX VNQ VPU VAW'
    sectors = tickers.split(' ')
    tickers = index_appender(tickers)
    all_tickers = tickers.split(' ')
    print(" ")
    print('Fetching Market Composite Index funds...')
    data, _ = download_data_indexes(indexes=all_tickers, tickers=tickers, period=period, interval='1d')
    print(" ")
    return data, sectors


def simple_beta_rsq(fund: pd.DataFrame, benchmark: pd.DataFrame, recent_period: list=[]) -> list:
    simple_br = []
    for period in recent_period:
        val = dict()
        val['period'] = period 
        tot_len = len(fund['Close'])
        b, r = beta_comparison_list(fund['Close'][tot_len-period:tot_len], benchmark['Close'][tot_len-period:tot_len])
        val['beta'] = np.round(b, 5) 
        val['r_squared'] = np.round(r, 5)
        simple_br.append(val.copy())
    return simple_br 


def composite_index(data: dict, sectors: list, progress_bar=None, plot_output=True):
    composite = []
    for tick in sectors:
        graph, _ = cluster_oscs(data[tick], plot_output=False, function='market', wma=False)
        progress_bar.uptick()
        composite.append(graph)

    composite2 = []
    for i in range(len(composite[0])):
        s = 0.0
        for j in range(len(composite)):
            s += float(composite[j][i])

        composite2.append(s)
    progress_bar.uptick()

    if plot_output:
        dual_plotting(data['^GSPC']['Close'], composite2, y1_label='S&P500', y2_label='MCI', title='Market Composite Index')
    else:
        dual_plotting(data['^GSPC']['Close'], composite2, y1_label='S&P500', y2_label='MCI', title='Market Composite Index', saveFig=True, filename='MCI.png')
    progress_bar.uptick()
    return composite2 


def composite_correlation(data: dict, sectors: list, composite_osc=None, progress_bar=None, plot_output=True) -> dict:
    """ betas and r-squared for 2 time periods for each sector (full, 1/2 time) """
    """ plot of r-squared vs. S&P500 for last 50 or 100 days for each sector """
    DIVISOR = 5
    correlations = {}

    if '^GSPC' in data.keys():
        tot_len = len(data['^GSPC']['Close'])
        start_pt = int(np.floor(tot_len / DIVISOR))
        if start_pt > 100:
            start_pt = 100
        corrs = {}
        dates = data['^GSPC'].index[start_pt:tot_len]
        net_correlation = [0.0] * (tot_len-start_pt)
        for sector in sectors:
            correlations[sector] = simple_beta_rsq(data[sector], data['^GSPC'], recent_period=[int(np.round(tot_len/2, 0)), tot_len])
            corrs[sector] = []
            for i in range(start_pt, tot_len):
                _, rsqd = beta_comparison_list(data[sector]['Close'][i-start_pt:i], data['^GSPC']['Close'][i-start_pt:i])
                corrs[sector].append(rsqd)
                net_correlation[i-start_pt] += rsqd
            progress_bar.uptick()

        plots = [corrs[x] for x in corrs.keys()]
        legend = [x for x in corrs.keys()]
        generic_plotting(plots, x_=dates, title='MCI Correlations', legend=legend, saveFig=(not plot_output), filename='MCI_correlations.png')
        progress_bar.uptick()

        max_ = np.max(net_correlation)
        net_correlation = [x / max_ for x in net_correlation]

        legend = ['Net Correlation', 'S&P500']
        dual_plotting(  net_correlation, 
                        data['^GSPC']['Close'][start_pt:tot_len], 
                        x=dates,
                        y1_label=legend[0], 
                        y2_label=legend[1], 
                        title='MCI Net Correlation', 
                        saveFig=(not plot_output), 
                        filename='MCI_net_correlation.png')
        
        progress_bar.uptick()

        if composite_osc is not None:
            osc_corr = []
            o_max = np.max(composite_osc)
            norm_osc = [x/o_max for x in composite_osc]
            o_max = np.max(net_correlation)
            norm_corr = [x/o_max for x in net_correlation]
            norm_mean = np.mean(norm_corr)
            for i in range(start_pt, tot_len):
                val = 0.0
                if norm_corr[i-start_pt] < norm_mean:
                    if norm_osc[i] > 0:
                        # Sell signal w/ weak net correlations:
                        val = norm_corr[i-start_pt] * norm_osc[i]
                else:
                    if norm_osc[i] < 0:
                        val = norm_corr[i-start_pt] * norm_osc[i]
                osc_corr.append(val)

            legend = ['Oscillator-Correlation', 'S&P500']
            dual_plotting(  osc_corr, 
                            data['^GSPC']['Close'][start_pt:tot_len], 
                            x=dates,
                            y1_label=legend[0], 
                            y2_label=legend[1], 
                            title='MCI Oscillator-Correlation', 
                            saveFig=(not plot_output), 
                            filename='MCI_osc_correlation.png')
            
        progress_bar.uptick()

    return correlations


def market_composite_index(config: dict=None, period=None, plot_output=False) -> dict:
    if config is not None:
        period = config['period']
        properties = config['properties']
    elif period is None:
        print(f"ERROR: config and period both provided {period} for market_composite_index")
        return {}
    else:
        # Support for release 1 versions
        period = period
        properties = dict()
        properties['Indexes'] = {}
        properties['Indexes']['Market Sector'] = True

    """ Validate each index key is set to True in the --core file """
    if properties is not None:
        if 'Indexes' in properties.keys():
            props = properties['Indexes']
            if 'Market Sector' in props.keys():
                if props['Market Sector'] == True:
                    mci = dict()
                    data, sectors = metrics_initializer(period=period)

                    p = ProgressBar(len(sectors)*2+5, name='Market Composite Index')
                    p.start()

                    composite = composite_index(data, sectors, plot_output=plot_output, progress_bar=p) 
                    mci['tabular'] = {'mci': composite}
                    correlations = composite_correlation(data, sectors, composite_osc=composite, plot_output=plot_output, progress_bar=p)
                    mci['tabular']['correlations'] = correlations
                    return mci
    return {}



def type_composite_index(data: pd.DataFrame, sectors: list, plot_output=True):
    """ Similar to MCI, TCI compares broader market types (sensitive, cyclical, and defensive) """
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

