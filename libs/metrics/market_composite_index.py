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
from libs.utils import TEXT_COLOR_MAP

ERROR_COLOR = TEXT_COLOR_MAP["red"]
NORMAL_COLOR = TEXT_COLOR_MAP["white"]


def metrics_initializer(period='2y', name='Market Composite Index'):
    """Metrics Initializer

    Keyword Arguments:
        duration {str} -- duration of view (default: {'long'})

    Returns:
        list -- data downloaded and sector list
    """
    tickers = 'VGT VHT VCR VDC VFH VDE VIS VOX VNQ VPU VAW'
    sectors = tickers.split(' ')
    tickers = index_appender(tickers)
    all_tickers = tickers.split(' ')
    print(" ")
    print(f'Fetching {name} funds...')
    data, _ = download_data_indexes(
        indexes=all_tickers, tickers=tickers, period=period, interval='1d')
    print(" ")
    return data, sectors


def simple_beta_rsq(fund: pd.DataFrame, benchmark: pd.DataFrame, recent_period: list = []) -> list:
    simple_br = []
    for period in recent_period:
        val = dict()
        val['period'] = period
        tot_len = len(fund['Close'])
        b, r = beta_comparison_list(
            fund['Close'][tot_len-period:tot_len], benchmark['Close'][tot_len-period:tot_len])
        val['beta'] = np.round(b, 5)
        val['r_squared'] = np.round(r, 5)
        simple_br.append(val.copy())
    return simple_br


def composite_index(data: dict, sectors: list, progress_bar=None, plot_output=True) -> list:
    """Composite Index

    Arguments:
        data {dict} -- data
        sectors {list} -- list of sectors

    Keyword Arguments:
        progress_bar {[type]} -- (default: {None})
        plot_output {bool} -- (default: {True})

    Returns:
        list -- correlation vector
    """
    composite = []
    for tick in sectors:
        graph, _ = cluster_oscs(
            data[tick], plot_output=False, function='market', wma=False)
        progress_bar.uptick()
        composite.append(graph)

    composite2 = []
    for i in range(len(composite[0])):
        s = 0.0
        for j in range(len(composite)):
            s += float(composite[j][i])

        composite2.append(s)
    progress_bar.uptick()

    max_ = np.max(np.abs(composite2))
    composite2 = [x / max_ for x in composite2]
    progress_bar.uptick()

    if plot_output:
        dual_plotting(data['^GSPC']['Close'], composite2, y1_label='S&P500',
                      y2_label='MCI', title='Market Composite Index')
    else:
        dual_plotting(data['^GSPC']['Close'], composite2, y1_label='S&P500', y2_label='MCI',
                      title='Market Composite Index', saveFig=True, filename='MCI.png')
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
            correlations[sector] = simple_beta_rsq(data[sector], data['^GSPC'], recent_period=[
                                                   int(np.round(tot_len/2, 0)), tot_len])
            corrs[sector] = []
            for i in range(start_pt, tot_len):
                _, rsqd = beta_comparison_list(
                    data[sector]['Close'][i-start_pt:i], data['^GSPC']['Close'][i-start_pt:i])
                corrs[sector].append(rsqd)
                net_correlation[i-start_pt] += rsqd
            progress_bar.uptick()

        plots = [corrs[x] for x in corrs.keys()]
        legend = [x for x in corrs.keys()]
        generic_plotting(plots, x=dates, title='MCI Correlations', legend=legend, saveFig=(
            not plot_output), filename='MCI_correlations.png')
        progress_bar.uptick()

        max_ = np.max(net_correlation)
        net_correlation = [x / max_ for x in net_correlation]

        legend = ['Net Correlation', 'S&P500']
        dual_plotting(net_correlation,
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
            dual_plotting(osc_corr,
                          data['^GSPC']['Close'][start_pt:tot_len],
                          x=dates,
                          y1_label=legend[0],
                          y2_label=legend[1],
                          title='MCI Oscillator-Correlation',
                          saveFig=(not plot_output),
                          filename='MCI_osc_correlation.png')

        progress_bar.uptick()

    return correlations


def market_composite_index(**kwargs) -> dict:
    """
    Market Composite Index (MCI)

    args:

    optional args:
        config:         (dict) controlling config dictionary; DEFAULT=None
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        period:         (str) time period for data (e.g. '2y'); DEFAULT=None

    returns:
        mci:            (dict) contains all mci information 
    """
    config = kwargs.get('config')
    period = kwargs.get('period')
    plot_output = kwargs.get('plot_output', True)

    if config is not None:
        period = config['period']
        properties = config['properties']
    elif period is None:
        print(
            f"{ERROR_COLOR}ERROR: config and period both provided {period} for market_composite_index{NORMAL_COLOR}")
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

                    p = ProgressBar(len(sectors)*2+7,
                                    name='Market Composite Index')
                    p.start()

                    composite = composite_index(
                        data, sectors, plot_output=plot_output, progress_bar=p)
                    mci['tabular'] = {'mci': composite}
                    correlations = composite_correlation(
                        data, sectors, composite_osc=composite, plot_output=plot_output, progress_bar=p)
                    mci['correlations'] = correlations
                    p.end()
                    return mci
    return {}


def type_composite_index(**kwargs):
    """ Similar to MCI, TCI compares broader market types (sensitive, cyclical, and defensive) """
    config = kwargs.get('config')
    period = kwargs.get('period')
    plot_output = kwargs.get('plot_output', True)

    if config is not None:
        period = config['period']
        properties = config['properties']
    elif period is None:
        print(
            f"{ERROR_COLOR}ERROR: config and period both provided {period} for type_composite_index{NORMAL_COLOR}")
        return {}
    else:
        # Support for release 1 versions
        period = period
        properties = dict()
        properties['Indexes'] = {}
        properties['Indexes']['Type Sector'] = True

    """ Validate each index key is set to True in the --core file """
    if properties is not None:
        if 'Indexes' in properties.keys():
            props = properties['Indexes']
            if 'Type Sector' in props.keys():
                if props['Type Sector'] == True:

                    data, sectors = metrics_initializer(
                        period='2y', name='Type Composite Index')

                    p = ProgressBar(13, name='Type Composite Index')
                    p.start()

                    tci = dict()
                    defensive = []
                    d_val = [25.0]
                    cyclical = []
                    c_val = [25.0]
                    sensitive = []
                    s_val = [25.0]

                    composite = {}
                    for sect in sectors:
                        graph, _ = cluster_oscs(
                            data[sect], plot_output=False, function='market', wma=False, progress_bar=p)
                        composite[sect] = graph

                    for i in range(len(composite['VGT'])):
                        d = float(composite['VHT'][i])
                        d += float(composite['VPU'][i])
                        d += float(composite['VDC'][i])
                        d += float(composite['VNQ'][i]) * 0.6
                        defensive.append(d)

                        c = float(composite['VNQ'][i]) * 0.4
                        c += float(composite['VCR'][i])
                        c += float(composite['VFH'][i])
                        c += float(composite['VAW'][i])
                        cyclical.append(c)

                        s = float(composite['VIS'][i])
                        s += float(composite['VOX'][i])
                        s += float(composite['VDE'][i])
                        s += float(composite['VGT'][i])
                        sensitive.append(s)

                        if i > 0:
                            d1 = (data['VHT']['Close'][i] - data['VHT']
                                  ['Close'][i-1]) / data['VHT']['Close'][i-1]
                            d2 = (data['VPU']['Close'][i] - data['VPU']
                                  ['Close'][i-1]) / data['VPU']['Close'][i-1]
                            d3 = (data['VDC']['Close'][i] - data['VDC']
                                  ['Close'][i-1]) / data['VDC']['Close'][i-1]
                            d4 = (data['VNQ']['Close'][i] - data['VNQ']
                                  ['Close'][i-1]) / data['VNQ']['Close'][i-1] * 0.6
                            d = (d1 + d2 + d3 + d4) / 3.6
                            d_val.append(d_val[-1] * (1.0 + d))

                            d1 = (data['VCR']['Close'][i] - data['VCR']
                                  ['Close'][i-1]) / data['VCR']['Close'][i-1]
                            d2 = (data['VFH']['Close'][i] - data['VFH']
                                  ['Close'][i-1]) / data['VFH']['Close'][i-1]
                            d3 = (data['VAW']['Close'][i] - data['VAW']
                                  ['Close'][i-1]) / data['VAW']['Close'][i-1]
                            d4 = (data['VNQ']['Close'][i] - data['VNQ']
                                  ['Close'][i-1]) / data['VNQ']['Close'][i-1] * 0.4
                            d = (d1 + d2 + d3 + d4) / 3.4
                            c_val.append(c_val[-1] * (1.0 + d))

                            d1 = (data['VIS']['Close'][i] - data['VIS']
                                  ['Close'][i-1]) / data['VIS']['Close'][i-1]
                            d2 = (data['VOX']['Close'][i] - data['VOX']
                                  ['Close'][i-1]) / data['VOX']['Close'][i-1]
                            d3 = (data['VDE']['Close'][i] - data['VDE']
                                  ['Close'][i-1]) / data['VDE']['Close'][i-1]
                            d4 = (data['VGT']['Close'][i] - data['VGT']
                                  ['Close'][i-1]) / data['VGT']['Close'][i-1]
                            d = (d1 + d2 + d3 + d4) / 4
                            s_val.append(s_val[-1] * (1.0 + d))

                    p.uptick()

                    tci['defensive'] = {
                        "tabular": d_val, "clusters": defensive}
                    tci['sensitive'] = {
                        "tabular": s_val, "clusters": sensitive}
                    tci['cyclical'] = {"tabular": c_val, "clusters": cyclical}

                    dates = data['VGT'].index
                    if plot_output:
                        dual_plotting(y1=d_val, y2=defensive, y1_label='Defensive Index',
                                      y2_label='Clustered Osc', title='Defensive Index', x=dates)
                        dual_plotting(y1=s_val, y2=sensitive, y1_label='Sensitive Index',
                                      y2_label='Clustered Osc', title='Sensitive Index', x=dates)
                        dual_plotting(y1=c_val, y2=cyclical, y1_label='Cyclical Index',
                                      y2_label='Clustered Osc', title='Cyclical Index', x=dates)
                        generic_plotting([d_val, s_val, c_val], legend=[
                            'Defensive', 'Sensitive', 'Cyclical'], title='Type Indexes', x=dates)
                    else:
                        generic_plotting([d_val, s_val, c_val], legend=['Defensive', 'Sensitive', 'Cyclical'], title='Type Indexes',
                                         x=dates, saveFig=True, ylabel='Normalized "Price"', filename='tci.png')

                    p.end()
                    return tci
    return {}
