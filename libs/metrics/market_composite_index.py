"""
market_composite_index.py

An equal-weight aggregate metric that takes the computed clustered oscillator metric 
for each of the 11 sectors of the market represented by the Vanguard ETFs listed under
'tickers' below in 'metrics_initializer'. Arguably a more accurate metric than a 
clustered oscillator metric on the S&P500 by itself. 

Newer - compares this metric with a correlation metric of each sector.
"""

import os
import json
import pandas as pd
import numpy as np

from libs.tools import cluster_oscs, beta_comparison_list
from libs.tools import windowed_moving_avg
from libs.utils import dual_plotting, generic_plotting
from libs.utils import ProgressBar, index_appender
from libs.utils import download_data_indexes
from libs.utils import STANDARD_COLORS

ERROR_COLOR = STANDARD_COLORS["error"]
WARNING = STANDARD_COLORS["warning"]
NORMAL_COLOR = STANDARD_COLORS["normal"]


def market_composite_index(**kwargs) -> dict:
    """Market Composite Index (MCI)

    Optional Args:
        config {dict} -- controlling config dictionary (default: {None})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        period {str / list} -- time period for data (e.g. '2y') (default: {None})
        clock {uint64_t} -- time for prog_bar (default: {None})
        data {pd.DataFrame} -- dataset with sector funds (default: {None})

    returns:
        list -- dict contains all mci information, dict fund content, sector list
    """
    config = kwargs.get('config')
    period = kwargs.get('period')
    clock = kwargs.get('clock')
    plot_output = kwargs.get('plot_output', True)
    data = kwargs.get('data')
    sectors = kwargs.get('sectors')

    if config is not None:
        period = config['period']
        properties = config['properties']

    elif period is None:
        print(
            f"{ERROR_COLOR}ERROR: config and period both provided {period} " +
            f"for market_composite_index{NORMAL_COLOR}")
        return {}

    else:
        # Support for release 1 versions
        period = period
        properties = dict()
        properties['Indexes'] = {}
        properties['Indexes']['Market Sector'] = True

    # Validate each index key is set to True in the --core file
    if properties is not None:
        if 'Indexes' in properties.keys():
            props = properties['Indexes']
            if 'Market Sector' in props.keys():
                if props['Market Sector'] == True:

                    mci = dict()
                    if data is None or sectors is None:
                        data, sectors = metrics_initializer(period=period)

                    if data:
                        p = ProgressBar(len(sectors)*2+5,
                                        name='Market Composite Index', offset=clock)
                        p.start()

                        composite = composite_index(
                            data, sectors, plot_output=plot_output, progress_bar=p)
                        correlations = composite_correlation(
                            data, sectors, plot_output=plot_output, progress_bar=p)

                        mci['tabular'] = {'mci': composite}
                        mci['correlations'] = correlations
                        p.end()

                        return mci, data, sectors
    return {}, None, None


def metrics_initializer(period='5y', name='Market Composite Index'):
    """Metrics Initializer

    Keyword Arguments:
        period {str/list} -- duration of view (default: {'5y'})
        name {str} -- (default: {'Market Composite Index'})

    Returns:
        list -- data downloaded, sector list
    """
    metrics_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(metrics_file):
        print(
            f"{WARNING}WARNING: '{metrics_file}' not found for " +
            f"'metrics_initializer'. Failed.{NORMAL_COLOR}")
        return None, []

    with open(metrics_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()
        m_data = m_data.get("Market_Composite")

    sectors = m_data['tickers']
    tickers = " ".join(m_data['tickers'])

    tickers = index_appender(tickers)
    all_tickers = tickers.split(' ')

    if isinstance(period, (list)):
        period = period[0]

    print(" ")
    print(f'Fetching {name} funds for {period}...')
    data, _ = download_data_indexes(
        indexes=all_tickers, tickers=tickers, period=period, interval='1d')
    print(" ")

    return data, sectors


def simple_beta_rsq(fund: pd.DataFrame, benchmark: pd.DataFrame, recent_period: list = []) -> list:
    """Simple Beta R-Squared

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        benchmark {pd.DataFrame} -- benchmark, typically S&P500 data set

    Keyword Arguments:
        recent_period {list} -- list of starting lookback periods (default: {[]})

    Returns:
        list -- list of beta/r-squared data objects
    """
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
        progress_bar {ProgressBar} -- (default: {None})
        plot_output {bool} -- (default: {True})

    Returns:
        list -- correlation vector
    """
    composite = []
    for tick in sectors:
        cluster = cluster_oscs(
            data[tick],
            plot_output=False,
            function='market',
            wma=False,
            progress_bar=progress_bar)

        graph = cluster['tabular']
        composite.append(graph)

    composite2 = []
    for i in range(len(composite[0])):
        s = 0.0
        for j in range(len(composite)):
            s += float(composite[j][i])

        composite2.append(s)

    progress_bar.uptick()

    composite2 = windowed_moving_avg(composite2, 3, data_type='list')

    max_ = np.max(np.abs(composite2))
    composite2 = [x / max_ for x in composite2]
    progress_bar.uptick()

    if plot_output:
        dual_plotting(data['^GSPC']['Close'], composite2, y1_label='S&P500',
                      y2_label='MCI', title='Market Composite Index')
    else:
        dual_plotting(data['^GSPC']['Close'], composite2, y1_label='S&P500', y2_label='MCI',
                      title='Market Composite Index', save_fig=True, filename='MCI.png')

    progress_bar.uptick()
    return composite2


def composite_correlation(data: dict, sectors: list, progress_bar=None, plot_output=True) -> dict:
    """Composite Correlation

    Betas and r-squared for 2 time periods for each sector (full, 1/2 time); plot of r-squared
    vs. S&P500 for last 50 or 100 days for each sector.

    Arguments:
        data {dict} -- data object
        sectors {list} -- list of sectors

    Keyword Arguments:
        progress_bar {ProgressBar} -- (default: {None})
        plot_output {bool} -- (default: {True})

    Returns:
        dict -- correlation dictionary
    """
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

        DIVISOR = 10.0
        increment = float(len(sectors)) / (float(tot_len -
                                                 start_pt) / DIVISOR * float(len(sectors)))

        counter = 0
        for sector in sectors:
            correlations[sector] = simple_beta_rsq(
                data[sector],
                data['^GSPC'],
                recent_period=[int(np.round(tot_len/2, 0)), tot_len]
            )

            corrs[sector] = []
            for i in range(start_pt, tot_len):

                _, rsqd = beta_comparison_list(
                    data[sector]['Close'][i-start_pt:i], data['^GSPC']['Close'][i-start_pt:i])

                corrs[sector].append(rsqd)
                net_correlation[i-start_pt] += rsqd

                counter += 1
                if counter == DIVISOR:
                    progress_bar.uptick(increment=increment)
                    counter = 0

        plots = [corrs[x] for x in corrs.keys()]
        legend = [x for x in corrs.keys()]

        generic_plotting(plots, x=dates, title='MCI Correlations', legend=legend, save_fig=(
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
                      save_fig=(not plot_output),
                      filename='MCI_net_correlation.png')

        progress_bar.uptick()

    return correlations
