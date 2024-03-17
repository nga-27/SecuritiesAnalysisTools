"""
bond_composite_index.py

An quasi-weighted aggregate metric that takes the computed clustered oscillator metric
for various bond types of the bond market represented by the Vanguard ETFs listed under
'tickers' below in 'metrics_initializer'. Note - bond oscillators are not as accurate
as market oscillators, but the metrics can still provide buy-sell signals.
"""
import os
import json
from typing import Tuple, Union, Dict

import pandas as pd
import numpy as np

from libs.tools import cluster_oscillators
from libs.tools.moving_averages_lib.windowed_moving_avg import windowed_moving_avg
from libs.utils import (
    generate_plot, ProgressBar, dates_extractor_list, download_data_indexes, STANDARD_COLORS,
    PlotType
)

WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]

BOND_NAME_MAP = {
    "Treasury": "Government"
}


def bond_composite_index(config: dict, **kwargs) -> None:
    """Bond Composite Index (BCI)

    Arguments:
        config {dict} -- controlling config dictionary

    Optional Args:
        plot_output {bool} -- True to render plot in realtime (default: {True})
        clock {float} -- time for prog_bar (default: {None})
    """
    # pylint: disable=too-many-branches,too-many-locals
    plot_output = kwargs.get('plot_output', True)
    clock = kwargs.get('clock')

    period = config['period']
    properties = config.get('properties', {})
    plots = []
    legend = []

    # Validate each index key is set to True in the --core file
    props: Dict[str, bool] = properties.get('Indexes', {})
    for bond_type in ('Treasury Bond', 'Corporate Bond', 'International Bond'):
        if props.get(bond_type, False):
            bond_type_name = bond_type.split(' ', maxsplit=1)[0]
            data, sectors, index_type, m_data = metrics_initializer(
                period=period, bond_type=bond_type_name)
            if m_data:
                _, data, dates = composite_index(data, sectors, m_data,
                                                    plot_output=plot_output,
                                                    bond_type=bond_type_name,
                                                    index_type=index_type,
                                                    clock=clock)
                plots.append(data)
                legend.append(bond_type_name)

    if len(plots) > 0:
        generate_plot(
            PlotType.GENERIC_PLOTTING, plots, **dict(
                x=dates, title='Bond Composite Indexes', legend=legend,
                ylabel='Normalized Price', plot_output=plot_output,
                filename="combined_BCI.png"
            )
        )


def metrics_initializer(period='2y',
                        bond_type='Treasury') -> Tuple[dict, list, str, Union[dict, None]]:
    """Metrics Initializer

    Keyword Arguments:
        period {str} -- (default: {'2y'})
        bond_type {str} -- (default: {'Treasury'})

    Returns:
        list -- downloaded_data, sector_list, index, metrics_file data
    """
    metrics_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(metrics_file):
        print(
            f"{WARNING}WARNING: '{metrics_file}' not found for " +
            f"'metrics_initializer'. Failed.{NORMAL}")
        return {}, [], '', None

    with open(metrics_file, 'r', encoding='utf-8') as m_file:
        m_data = json.load(m_file)
        m_file.close()
        m_data = m_data.get("Bond_Weight")

    data = m_data[bond_type]
    tickers = list(data.keys())
    tickers = ' '.join(tickers)
    index = BOND_NAME_MAP.get(bond_type, bond_type)

    if isinstance(period, (list)):
        period = period[0]

    sectors = tickers.split(' ')
    print(" ")
    print(f'Fetching {bond_type} Bond Composite Index funds for {period}...')
    data, _ = download_data_indexes(
        indexes=sectors, tickers=tickers, period=period, interval='1d')
    print(" ")
    return data, sectors, index, m_data


def bond_type_index_generator(data: pd.DataFrame, m_data: dict, bond_type='Treasury') -> list:
    """Bond Type Index Generator

    Arguments:
        data {pd.DataFrame} -- fund dataset
        m_data {dict} -- bond content from sectors.json

    Keyword Arguments:
        bond_type {str} -- Either 'Treasury', 'International', or 'Corporate'
            (default: {'Treasury'})

    Returns:
        list -- the bond type index
    """
    weights = m_data[bond_type]
    key_start = list(weights.keys())[0]
    index_chart = [25.0]
    for i in range(1, len(data[key_start]['Close'])):
        base = 0.0
        for tick in weights:
            val = (data[tick]['Close'][i] - data[tick]
                   ['Close'][i-1]) / data[tick]['Close'][i-1]
            val *= weights[tick]
            base += val

        base = index_chart[-1] * (1.0 + base)
        index_chart.append(base)
    return index_chart


# pylint: disable=too-many-arguments
def composite_index(data: dict,
                    sectors: list,
                    index_dict: dict,
                    plot_output=True,
                    bond_type='Treasury',
                    index_type='BND',
                    **kwargs) -> Tuple[list, list, list]:
    """Composite Index

    Arguments:
        data {dict} -- Data of composites
        sectors {list} -- sector list
        index_dict {dict} -- data pulled from sectors.json file (can be None)

    Keyword Arguments:
        plot_output {bool} -- (default: {True})
        bond_type {str} -- (default: {'Treasury'})
        index_type {str} -- (default: {'BND'})

    Optional Args:
        clock {uint64_t} -- timekeeping for prog_bar (default: {None})

    Returns:
        list -- composite signal, plots, dates
    """
    # pylint: disable=too-many-locals
    clock = kwargs.get('clock')

    progress = len(sectors) + 2
    prog_bar = ProgressBar(progress, name=f'{bond_type} Bond Composite Index', offset=clock)
    prog_bar.start()

    composite = []
    for tick in sectors:
        if tick != index_type:
            cluster = cluster_oscillators(
                data[tick], plot_output=False, function='market', wma=False)
            graph = cluster['tabular']
            prog_bar.uptick()
            composite.append(graph)

    composite2 = []
    for i in range(len(composite[0])):
        s_val = 0.0
        for j_val in composite:
            s_val += float(j_val[i])

        composite2.append(s_val)
    prog_bar.uptick()

    composite2 = windowed_moving_avg(composite2, 3, data_type='list')
    max_ = np.max(np.abs(composite2))
    composite2 = [x / max_ for x in composite2]

    key = list(data.keys())[0]
    data_to_plot = bond_type_index_generator(
        data, index_dict, bond_type=bond_type)
    dates = dates_extractor_list(data[key])

    generate_plot(
        PlotType.DUAL_PLOTTING,
        data_to_plot,
        **{
            "y_list_2": composite2,
            "y1_label": index_type,
            "y2_label": "BCI",
            "title": f"{bond_type} Bond Composite Index",
            "x": dates,
            "filename": f"{bond_type}_BCI.png",
            "plot_output": plot_output
        }
    )

    prog_bar.uptick()

    return composite2, data_to_plot, dates
