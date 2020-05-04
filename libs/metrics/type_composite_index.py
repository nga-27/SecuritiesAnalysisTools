import os
import json
import pandas as pd
import numpy as np

from libs.tools import cluster_oscs
from libs.tools import windowed_moving_avg
from libs.utils import download_data_indexes
from libs.utils import dual_plotting, generic_plotting
from libs.utils import ProgressBar, index_appender
from libs.utils import STANDARD_COLORS

ERROR_COLOR = STANDARD_COLORS["error"]
WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]


def type_composite_index(**kwargs):
    """Type Composite Index (MCI)

    Similar to MCI, TCI compares broader market types (sensitive, cyclical, and defensive)

    Optional Args:
        config {dict} -- controlling config dictionary (default: {None})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        period {str / list} -- time period for data (e.g. '2y') (default: {None})
        clock {float} -- time for prog_bar (default: {None})

    returns:
        dict -- contains all tci information 
    """
    config = kwargs.get('config')
    period = kwargs.get('period')
    plot_output = kwargs.get('plot_output', True)
    clock = kwargs.get('clock')

    if config is not None:
        period = config['period']
        properties = config['properties']

    elif period is None:
        print(
            f"{ERROR_COLOR}ERROR: config and period both provided {period} " +
            f"for type_composite_index{NORMAL}")
        return {}

    else:
        # Support for release 1 versions
        period = period
        properties = dict()
        properties['Indexes'] = {}
        properties['Indexes']['Type Sector'] = True

    #  Validate each index key is set to True in the --core file
    if properties is not None:
        if 'Indexes' in properties.keys():
            props = properties['Indexes']
            if 'Type Sector' in props.keys():
                if props['Type Sector'] == True:

                    data, sectors, m_data = metrics_initializer(period='2y')

                    if data:
                        p = ProgressBar(
                            19, name='Type Composite Index', offset=clock)
                        p.start()

                        tci = dict()

                        composite = {}
                        for sect in sectors:
                            cluster = cluster_oscs(
                                data[sect],
                                plot_output=False,
                                function='market',
                                wma=False,
                                progress_bar=p
                            )

                            graph = cluster['tabular']
                            composite[sect] = graph

                        defensive = type_composites(
                            composite, m_data, type_type='Defensive')
                        p.uptick()

                        sensitive = type_composites(
                            composite, m_data, type_type='Sensitive')
                        p.uptick()

                        cyclical = type_composites(
                            composite, m_data, type_type='Cyclical')
                        p.uptick()

                        d_val = weighted_signals(
                            data, m_data, type_type='Defensive')
                        p.uptick()

                        s_val = weighted_signals(
                            data, m_data, type_type='Sensitive')
                        p.uptick()

                        c_val = weighted_signals(
                            data, m_data, type_type='Cyclical')
                        p.uptick()

                        d_val = windowed_moving_avg(d_val, 3, data_type='list')
                        c_val = windowed_moving_avg(c_val, 3, data_type='list')
                        s_val = windowed_moving_avg(s_val, 3, data_type='list')
                        p.uptick()

                        tci['defensive'] = {
                            "tabular": d_val,
                            "clusters": defensive
                        }
                        tci['sensitive'] = {
                            "tabular": s_val,
                            "clusters": sensitive
                        }
                        tci['cyclical'] = {
                            "tabular": c_val,
                            "clusters": cyclical
                        }

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
                            generic_plotting(
                                [d_val, s_val, c_val],
                                legend=['Defensive', 'Sensitive', 'Cyclical'],
                                title='Type Indexes',
                                x=dates,
                                saveFig=True,
                                ylabel='Normalized "Price"',
                                filename='tci.png'
                            )

                        p.end()
                        return tci
    return {}


def metrics_initializer(period='2y'):
    """Metrics Initializer

    Keyword Arguments:
        period {str} -- (default: {'2y'})

    Returns:
        list -- downloaded_data, sector_list, index, metrics_file data
    """
    metrics_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(metrics_file):
        print(
            f"{WARNING}WARNING: '{metrics_file}' not found for " +
            f"'metrics_initializer'. Failed.{NORMAL}")
        return None, [], None

    with open(metrics_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()
        m_data = m_data.get("Type_Composite")

    sectors = m_data['Components']
    tickers = " ".join(sectors)
    tickers = index_appender(tickers)
    all_tickers = tickers.split(' ')

    if isinstance(period, (list)):
        period = period[0]

    # tickers = index_appender(tickers)
    print(" ")
    print(f'Fetching Type Composite Index funds for {period}...')
    data, _ = download_data_indexes(
        indexes=sectors, tickers=all_tickers, period=period, interval='1d')
    print(" ")

    return data, sectors, m_data


def type_composites(composite: dict, m_data: dict, type_type='Defensive') -> list:
    """Type Composites

    Create the summed clustered composites

    Arguments:
        composite {dict} -- composite dictionary
        m_data {dict} -- data from sectors.json

    Keyword Arguments:
        type_type {str} -- key for each m_data (default: {'Defensive'})

    Returns:
        list -- summed list of composites
    """
    sector_data = m_data[type_type]
    start_key = list(sector_data.keys())[0]
    new_composite = []

    for i in range(len(composite[start_key])):
        value = 0.0
        for fund in sector_data:
            value += float(composite[fund][i]) * sector_data[fund]

        new_composite.append(value)

    return new_composite


def weighted_signals(data: dict, m_data: dict, type_type='Defensive') -> list:
    """Weighted Signals

    Arguments:
        data {dict} -- tci data object
        m_data {dict} -- sectors.json content

    Keyword Arguments:
        type_type {str} -- (default: {'Defensive'})

    Returns:
        list -- weighted signal
    """
    sector_data = m_data[type_type]
    start_key = list(sector_data.keys())[0]
    new_composite = [25.0]

    for i in range(1, len(data[start_key]['Close'])):
        value = 0.0
        for fund in sector_data:
            value += (data[fund]['Close'][i] - data[fund]['Close'][i-1]) /\
                data[fund]['Close'][i-1] * sector_data[fund]

        value = new_composite[-1] * (1.0 + value)
        new_composite.append(value)

    return new_composite
