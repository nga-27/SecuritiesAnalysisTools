""" type composite index """
import os
import json
from typing import Tuple, Union

from libs.tools import cluster_oscillators, windowed_moving_avg
from libs.utils import (
    download_data_indexes, dual_plotting, generic_plotting, ProgressBar, index_appender,
    STANDARD_COLORS
)

ERROR_COLOR = STANDARD_COLORS["error"]
WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]


def type_composite_index(**kwargs) -> Tuple[dict, Union[dict, None], Union[list, None]]:
    """Type Composite Index (MCI)

    Similar to MCI, TCI compares broader market types (sensitive, cyclical, and defensive)

    Optional Args:
        config {dict} -- controlling config dictionary (default: {None})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        period {str / list} -- time period for data (e.g. '2y') (default: {None})
        clock {float} -- time for prog_bar (default: {None})
        data {pd.DataFrame} -- fund datasets (default: {None})
        sectors {list} -- list of sectors (default: {None})

    returns:
        list -- dict contains all tci information, data, sectors
    """
    # pylint: disable=too-many-locals,too-many-statements,too-many-nested-blocks
    config = kwargs.get('config')
    period = kwargs.get('period')
    plot_output = kwargs.get('plot_output', True)
    clock = kwargs.get('clock')
    data = kwargs.get('data')
    sectors = kwargs.get('sectors')

    if config is not None:
        period = config['period']
        properties = config['properties']

    elif period is None:
        print(
            f"{ERROR_COLOR}ERROR: config and period both provided {period} " +
            f"for type_composite_index{NORMAL}")
        return {}, None, None

    else:
        # Support for release 1 versions
        properties = {}
        properties['Indexes'] = {}
        properties['Indexes']['Type Sector'] = True

    #  Validate each index key is set to True in the --core file
    if properties is not None:
        if 'Indexes' in properties.keys():
            props = properties['Indexes']
            if 'Type Sector' in props.keys():
                if props['Type Sector']:
                    m_data = get_metrics_content()
                    if data is None or sectors is None:
                        data, sectors = metrics_initializer(
                            m_data, period='2y')

                    if data:
                        prog_bar = ProgressBar(
                            19, name='Type Composite Index', offset=clock)
                        prog_bar.start()

                        tci = {}
                        composite = {}
                        for sect in sectors:
                            cluster = cluster_oscillators(
                                data[sect],
                                plot_output=False,
                                function='market',
                                wma=False,
                                progress_bar=prog_bar
                            )

                            graph = cluster['tabular']
                            composite[sect] = graph

                        defensive = type_composites(
                            composite, m_data, type_type='Defensive')
                        prog_bar.uptick()

                        sensitive = type_composites(
                            composite, m_data, type_type='Sensitive')
                        prog_bar.uptick()

                        cyclical = type_composites(
                            composite, m_data, type_type='Cyclical')
                        prog_bar.uptick()

                        d_val = weighted_signals(
                            data, m_data, type_type='Defensive')
                        prog_bar.uptick()

                        s_val = weighted_signals(
                            data, m_data, type_type='Sensitive')
                        prog_bar.uptick()

                        c_val = weighted_signals(
                            data, m_data, type_type='Cyclical')
                        prog_bar.uptick()

                        d_val = windowed_moving_avg(d_val, 3, data_type='list')
                        c_val = windowed_moving_avg(c_val, 3, data_type='list')
                        s_val = windowed_moving_avg(s_val, 3, data_type='list')
                        prog_bar.uptick()

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
                                          y2_label='Clustered Osc', title='Defensive Index',
                                          x=dates)
                            dual_plotting(y1=s_val, y2=sensitive, y1_label='Sensitive Index',
                                          y2_label='Clustered Osc', title='Sensitive Index',
                                          x=dates)
                            dual_plotting(y1=c_val, y2=cyclical, y1_label='Cyclical Index',
                                          y2_label='Clustered Osc', title='Cyclical Index',
                                          x=dates)
                            generic_plotting([d_val, s_val, c_val],
                                              legend=['Defensive', 'Sensitive', 'Cyclical'],
                                              title='Type Indexes', x=dates)
                        else:
                            generic_plotting(
                                [d_val, s_val, c_val],
                                legend=['Defensive', 'Sensitive', 'Cyclical'],
                                title='Type Indexes',
                                x=dates,
                                save_fig=True,
                                ylabel='Normalized "Price"',
                                filename='tci.png'
                            )

                        prog_bar.end()
                        return tci, data, sectors
    return {}, None, None


def metrics_initializer(m_data: dict, period='2y'):
    """Metrics Initializer

    Keyword Arguments:
        period {str} -- (default: {'2y'})

    Returns:
        list -- downloaded_data, sector_list, index, metrics_file data
    """
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

    return data, sectors


def get_metrics_content() -> dict:
    """Get Metrics Content

    Returns:
        dict -- metrics file data
    """
    metrics_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(metrics_file):
        print(
            f"{WARNING}WARNING: '{metrics_file}' not found for " +
            f"'metrics_initializer'. Failed.{NORMAL}")
        return None, [], None

    with open(metrics_file, encoding='utf-8') as m_file:
        m_data = json.load(m_file)
        m_file.close()
        m_data = m_data.get("Type_Composite")

    return m_data


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
