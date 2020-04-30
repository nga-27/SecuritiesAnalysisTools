"""
bond_composite_index.py

An quasi-weighted aggregate metric that takes the computed clustered oscillator metric 
for various bond types of the bond market represented by the Vanguard ETFs listed under
'tickers' below in 'metrics_initializer'. Note - bond oscillators are not as accurate 
as market oscillators, but the metrics can still provide buy-sell signals.
"""

import pandas as pd
import numpy as np

from libs.tools import cluster_oscs, windowed_moving_avg
from libs.utils import dual_plotting, generic_plotting
from libs.utils import ProgressBar, index_appender, dates_extractor_list
from libs.utils import download_data_indexes


def metrics_initializer(period='2y', bond_type='Treasury'):
    """Metrics Initializer

    Keyword Arguments:
        period {str} -- (default: {'2y'})
        bond_type {str} -- (default: {'Treasury'})

    Returns:
        list -- downloaded_data, sector_list, index
    """
    if bond_type == 'Treasury':
        # Treasury (Gov't only - general alternative would be BSV/BIV/BLV)
        tickers = 'VGSH VGLT VGIT VTEB VMBS'
        index = 'Government'

    elif bond_type == 'Corporate':
        # Corporate investment-grade bonds (BBB/BAA or higher)
        tickers = 'VCSH VCIT VCLT'
        index = 'Corporate'

    elif bond_type == 'International':
        # BNDX - International investment grade: (roughly) 55% Europe, 25% Pacific, 10% N. America,
        #           4% Emerging
        # VWOB - Emerging Gov't: <45% below investment grade, 60% emerging markets
        tickers = 'BNDX VWOB'
        index = 'International'

    else:
        tickers = 'BND'

    if isinstance(period, (list)):
        period = period[0]

    sectors = tickers.split(' ')
    # tickers = index_appender(tickers)
    print(" ")
    print(f'Fetching {bond_type} Bond Composite Index funds for {period}...')
    data, _ = download_data_indexes(
        indexes=sectors, tickers=tickers, period=period, interval='1d')
    print(" ")
    return data, sectors, index


def treasury_index_generator(data: pd.DataFrame) -> list:
    """Treasury Index Generator

    Arguments:
        data {pd.DataFrame} -- data with corp bond tickers

    Returns:
        list -- corp bond index
    """
    SH_WEIGHT = 0.5
    IN_WEIGHT = 0.18
    LN_WEIGHT = 0.12
    MB_WEIGHT = 0.15
    MN_WEIGHT = 0.05

    index_chart = [25.0]
    for i in range(1, len(data['VGSH']['Close'])):
        v1 = (data['VGSH']['Close'][i] - data['VGSH']
              ['Close'][i-1]) / data['VGSH']['Close'][i-1]
        v1 *= SH_WEIGHT
        v2 = (data['VGIT']['Close'][i] - data['VGIT']
              ['Close'][i-1]) / data['VGIT']['Close'][i-1]
        v2 *= IN_WEIGHT
        v3 = (data['VGLT']['Close'][i] - data['VGLT']
              ['Close'][i-1]) / data['VGLT']['Close'][i-1]
        v3 *= LN_WEIGHT
        v4 = (data['VMBS']['Close'][i] - data['VMBS']
              ['Close'][i-1]) / data['VMBS']['Close'][i-1]
        v4 *= MB_WEIGHT
        v5 = (data['VTEB']['Close'][i] - data['VTEB']
              ['Close'][i-1]) / data['VTEB']['Close'][i-1]
        v5 *= MN_WEIGHT

        val = v1 + v2 + v3 + v4 + v5
        val = index_chart[-1] * (1.0 + val)
        index_chart.append(val)
    return index_chart


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
    progress = len(sectors) + 2
    p = ProgressBar(progress, name=f'{bond_type} Bond Composite Index')
    p.start()

    composite = []
    for tick in sectors:
        if tick != index_type:
            cluster = cluster_oscs(
                data[tick], plot_output=False, function='market', wma=False)
            graph = cluster['tabular']
            p.uptick()
            composite.append(graph)

    composite2 = []
    for i in range(len(composite[0])):
        s = 0.0
        for j in range(len(composite)):
            s += float(composite[j][i])

        composite2.append(s)
    p.uptick()

    composite2 = windowed_moving_avg(composite2, 3, data_type='list')
    max_ = np.max(np.abs(composite2))
    composite2 = [x / max_ for x in composite2]

    if bond_type == 'International':
        data_to_plot = international_index_generator(data)
        dates = dates_extractor_list(data['BNDX'])
    elif bond_type == 'Corporate':
        data_to_plot = corporate_index_generator(data)
        dates = dates_extractor_list(data['VCIT'])
    elif bond_type == 'Treasury':
        data_to_plot = treasury_index_generator(data)
        dates = dates_extractor_list(data['VGIT'])

    if plot_output:
        dual_plotting(data_to_plot, composite2, y1_label=index_type,
                      y2_label='BCI', title=f'{bond_type} Bond Composite Index')
    else:
        dual_plotting(data_to_plot, composite2,
                      y1_label=index_type, y2_label='BCI',
                      title=f'{bond_type} Bond Composite Index', x=dates,
                      saveFig=True, filename=f'{bond_type}_BCI.png')
    p.uptick()

    return composite2, data_to_plot, dates


def bond_composite_index(config: dict, **kwargs):
    """Bond Composite Index (BCI)

    Arguments:
        config {dict} -- controlling config dictionary

    Optional Args:
        plot_output {bool} -- True to render plot in realtime (default: {True})
    """
    plot_output = kwargs.get('plot_output', True)

    period = config['period']
    properties = config['properties']
    plots = []
    legend = []

    # Validate each index key is set to True in the --core file
    if properties is not None:
        if 'Indexes' in properties:
            props = properties['Indexes']
            if 'Treasury Bond' in props:
                if props['Treasury Bond'] == True:
                    data, sectors, index_type = metrics_initializer(
                        period=period, bond_type='Treasury')
                    _, data, dates = composite_index(data, sectors,
                                                     plot_output=plot_output,
                                                     bond_type='Treasury',
                                                     index_type=index_type)
                    plots.append(data)
                    legend.append("Treasury")

            if 'Corporate Bond' in props:
                if props['Corporate Bond'] == True:
                    data, sectors, index_type = metrics_initializer(
                        period=period, bond_type='Corporate')
                    _, data, dates = composite_index(data, sectors,
                                                     plot_output=plot_output,
                                                     bond_type='Corporate',
                                                     index_type=index_type)
                    plots.append(data)
                    legend.append("Corporate")

            if 'International Bond' in props:
                if props['International Bond'] == True:
                    data, sectors, index_type = metrics_initializer(
                        period=period, bond_type='International')
                    _, data, dates = composite_index(data, sectors,
                                                     plot_output=plot_output,
                                                     bond_type='International',
                                                     index_type=index_type)
                    plots.append(data)
                    legend.append("International")

            if len(plots) > 0:
                if plot_output:
                    generic_plotting(
                        plots, x=dates, title='Bond Composite Indexes',
                        legend=legend, ylabel='Normalized Price')
                else:
                    filename = f"combined_BCI.png"
                    generic_plotting(
                        plots, x=dates, title='Bond Composite Indexes',
                        legend=legend, saveFig=True, filename=filename,
                        ylabel='Normalized Price')
