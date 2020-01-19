"""
bond_composite_index.py

An quasi-weighted aggregate metric that takes the computed clustered oscillator metric 
for various bond types of the bond market represented by the Vanguard ETFs listed under
'tickers' below in 'metrics_initializer'. Note - bond oscillators are not as accurate 
as market oscillators, but the metrics can still provide buy-sell signals.
"""

import pandas as pd
import numpy as np

from libs.tools import cluster_oscs
from libs.utils import dual_plotting, ProgressBar, index_appender, dates_extractor_list
from libs.utils import download_data_indexes


def metrics_initializer(period='1y', bond_type='Treasury'):
    """Metrics Initializer

    Keyword Arguments:
        period {str} -- (default: {'1y'})
        bond_type {str} -- (default: {'Treasury'})

    Returns:
        list -- downloaded_data, sector_list, index
    """
    if bond_type == 'Treasury':
        # Treasury (Gov't only - alternative would be BSV/BIV/BLV)
        tickers = 'VGSH VGIT VGLT VTEB BND'
        index = 'BND'
    elif bond_type == 'Corporate':
        # Corporate investment-grade bonds (BBB/BAA or higher)
        tickers = 'VCSH VCIT VCLT'
        index = 'Corporate'
    elif bond_type == 'International':
        # BNDX - International investment grade: (roughly) 55% Europe, 25% Pacific, 10% N. America, 4% Emerging
        # VWOB - Emerging Gov't: <45% below investment grade, 60% emerging markets
        tickers = 'BNDX VWOB'
        index = 'International'
    else:
        tickers = 'BND'

    sectors = tickers.split(' ')
    # tickers = index_appender(tickers)
    print(" ")
    print(f'Fetching {bond_type} Bond Composite Index funds...')
    data, _ = download_data_indexes(
        indexes=sectors, tickers=tickers, period=period, interval='1d')
    print(" ")
    return data, sectors, index


def international_index_generator(data: pd.DataFrame) -> list:
    """International Index Generator

    Arguments:
        data {pd.DataFrame} -- Data set (with BNDX, VWOB)

    Returns:
        list -- the international bond index
    """
    BNDX_WEIGHT = 0.85
    VWOB_WEIGHT = 0.15
    index_chart = [25.0]
    for i in range(1, len(data['BNDX']['Close'])):
        v1 = (data['BNDX']['Close'][i] - data['BNDX']
              ['Close'][i-1]) / data['BNDX']['Close'][i-1]
        v1 *= BNDX_WEIGHT
        v2 = (data['VWOB']['Close'][i] - data['VWOB']
              ['Close'][i-1]) / data['VWOB']['Close'][i-1]
        v2 *= VWOB_WEIGHT
        val = v1 + v2
        val = index_chart[-1] * (1.0 + val)
        index_chart.append(val)
    return index_chart


def corporate_index_generator(data: pd.DataFrame) -> list:
    """Corporate Index Generator

    Arguments:
        data {pd.DataFrame} -- data with corp bond tickers

    Returns:
        list -- corp bond index
    """
    VCIT_WEIGHT = 0.2935
    VCSH_WEIGHT = 0.3666
    VCLT_WEIGHT = 0.3398
    index_chart = [25.0]
    for i in range(1, len(data['VCLT']['Close'])):
        v1 = (data['VCLT']['Close'][i] - data['VCLT']
              ['Close'][i-1]) / data['VCLT']['Close'][i-1]
        v2 = (data['VCIT']['Close'][i] - data['VCIT']
              ['Close'][i-1]) / data['VCIT']['Close'][i-1]
        v3 = (data['VCSH']['Close'][i] - data['VCSH']
              ['Close'][i-1]) / data['VCSH']['Close'][i-1]
        val = (v1 * VCLT_WEIGHT) + (v2 * VCIT_WEIGHT) + (v3 * VCSH_WEIGHT)
        val = index_chart[-1] * (1.0 + val)
        index_chart.append(val)
    return index_chart


def composite_index(data: dict, sectors: list, plot_output=True, bond_type='Treasury', index_type='BND'):
    """Composite Index

    Arguments:
        data {dict} -- Data of composites
        sectors {list} -- sector list

    Keyword Arguments:
        plot_output {bool} -- (default: {True})
        bond_type {str} -- (default: {'Treasury'})
        index_type {str} -- (default: {'BND'})

    Returns:
        [type] -- [description]
    """
    progress = len(sectors) + 1
    if (bond_type == 'International') or (bond_type == 'Corporate'):
        progress += 1
    p = ProgressBar(progress, name=f'{bond_type} Bond Composite Index')
    p.start()

    composite = []
    for tick in sectors:
        if tick != index_type:
            graph, _ = cluster_oscs(
                data[tick], plot_output=False, function='market', wma=False)
            p.uptick()
            composite.append(graph)

    composite2 = []
    for i in range(len(composite[0])):
        s = 0.0
        for j in range(len(composite)):
            s += float(composite[j][i])

        composite2.append(s)
    p.uptick()

    max_ = np.max(np.abs(composite2))
    composite2 = [x / max_ for x in composite2]

    if bond_type == 'International':
        data_to_plot = international_index_generator(data)
        dates = dates_extractor_list(data['BNDX'])
    elif bond_type == 'Corporate':
        data_to_plot = corporate_index_generator(data)
        dates = dates_extractor_list(data['VCIT'])
    else:
        data_to_plot = data[index_type]['Close']
        dates = []

    if plot_output:
        dual_plotting(data_to_plot, composite2, y1_label=index_type,
                      y2_label='BCI', title=f'{bond_type} Bond Composite Index')
    else:
        dual_plotting(data_to_plot, composite2,
                      y1_label=index_type, y2_label='BCI',
                      title=f'{bond_type} Bond Composite Index', x=dates,
                      saveFig=True, filename=f'{bond_type}_BCI.png')
    p.uptick()
    return composite2


def bond_composite_index(config: dict, **kwargs):
    """
    Bond Composite Index (BCI)

    args:
        config:         (dict) controlling config dictionary; DEFAULT=None

    optional args:
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True

    returns:
        None
    """
    plot_output = kwargs.get('plot_output', True)

    period = config['period']
    properties = config['properties']

    """ Validate each index key is set to True in the --core file """
    if properties is not None:
        if 'Indexes' in properties.keys():
            props = properties['Indexes']
            if 'Treasury Bond' in props.keys():
                if props['Treasury Bond'] == True:
                    data, sectors, index_type = metrics_initializer(
                        period=period, bond_type='Treasury')
                    composite_index(data, sectors, plot_output=plot_output,
                                    bond_type='Treasury', index_type=index_type)

            if 'Corporate Bond' in props.keys():
                if props['Corporate Bond'] == True:
                    data, sectors, index_type = metrics_initializer(
                        period=period, bond_type='Corporate')
                    composite_index(data, sectors, plot_output=plot_output,
                                    bond_type='Corporate', index_type=index_type)

            if 'International Bond' in props.keys():
                if props['International Bond'] == True:
                    data, sectors, index_type = metrics_initializer(
                        period=period, bond_type='International')
                    composite_index(data, sectors, plot_output=plot_output,
                                    bond_type='International', index_type=index_type)
