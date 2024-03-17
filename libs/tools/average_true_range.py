""" Average True Range """
import os
from typing import Union

import pandas as pd

from libs.utils import generate_plot, PlotType, INDEXES
from libs.utils.progress_bar import ProgressBar, update_progress_bar
from libs.features import normalize_signals
from .moving_averages_lib.exponential_moving_avg import exponential_moving_avg


def average_true_range(fund: pd.DataFrame, **kwargs) -> dict:
    """Average True Range

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})
        out_suppress {bool} -- prevents any plotting operations (default: {False})

    Returns:
        dict -- atr data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar: Union[ProgressBar, None] = kwargs.get('progress_bar')
    out_suppress = kwargs.get('out_suppress', False)

    atr = {}
    atr['tabular'] = get_atr_signal(
        fund, plot_output=plot_output, name=name, views=views, out_suppress=out_suppress)

    atr = atr_indicators(fund, atr, plot_output=plot_output, name=name, out_suppress=out_suppress)
    atr['length_of_signal'] = len(atr['tabular'])
    atr['type'] = 'oscillator'

    update_progress_bar(p_bar)

    return atr


def get_atr_signal(fund: pd.DataFrame, **kwargs) -> list:
    """Get ATR Signal

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        period {int} -- lookback period of atr signal (default: {14})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})
        out_suppress {bool} -- (default: {False})

    Returns:
        list -- atr signal
    """
    # pylint: disable=too-many-locals
    period = kwargs.get('period', 14)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    out_suppress = kwargs.get('out_suppress', False)

    signal = [0.0] * len(fund['Close'])

    atr = [0.0]
    for i in range(1, len(fund['Close'])):
        trues = [
            fund['High'][i] - fund['Low'][i],
            abs(fund['High'][i] - fund['Close'][i-1]),
            abs(fund['Low'][i] - fund['Close'][i-1])
        ]
        _max = max(trues)
        atr.append(_max)

    for i in range(period-1, len(fund['Close'])):
        atr_val = sum(atr[i-(period-1):i+1]) / float(period)
        signal[i] = atr_val

    if not out_suppress:
        name2 = INDEXES.get(name, name)
        title = f"{name2} - Average True Range"

        generate_plot(
            PlotType.DUAL_PLOTTING,
            fund['Close'],
            **{
                "y_list_2": signal,
                "y1_label": 'Price',
                "y2_label": 'ATR',
                "title": title,
                "filename": os.path.join(name, views, f"atr_{name}.png"),
                "plot_output": plot_output
            }
        )

    return signal


def atr_indicators(fund: pd.DataFrame, atr_dict: dict, **kwargs) -> dict:
    """ATR Indicators

    Run exponential moving average periods to weed out higher volatility: 20, 40

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        atr_dict {dict} -- atr data object

    Optional Args:
        periods {list} -- list of ema lookback periods (default: {[20, 40]})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        out_suppress {bool} -- (default: {False})

    Returns:
        dict: average_true_range dict
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements,chained-comparison
    periods = kwargs.get('periods', [50, 200])
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    out_suppress = kwargs.get('out_suppress', False)

    ema_1 = exponential_moving_avg(
        atr_dict['tabular'], periods[0], data_type='list')
    ema_2 = exponential_moving_avg(
        atr_dict['tabular'], periods[1], data_type='list')

    if len(ema_1) == 0 or len(ema_2) == 0:
        atr_dict['metrics'] = []
        atr_dict['signals'] = []
        return atr_dict

    states = []
    for i, tab in enumerate(atr_dict['tabular']):
        if tab > ema_1[i] and ema_1[i] > ema_2[i]:
            states.append('u3')
        elif tab > ema_1[i] and tab > ema_2[i]:
            states.append('u2')
        elif tab < ema_1[i] and tab > ema_2[i]:
            states.append('u1')
        elif tab > ema_1[i] and tab < ema_2[i]:
            states.append('e1')
        elif tab < ema_1[i] and ema_1[i] < ema_2[i]:
            states.append('e3')
        elif tab < ema_1[i] and tab < ema_2[i]:
            states.append('e2')
        else:
            states.append('n')

    metrics = [0.0] * len(ema_1)
    signals = []
    for i in range(1, len(ema_1)):
        date = fund.index[i].strftime("%Y-%m-%d")
        data = None

        if states[i] == 'u3' and states[i-1] != 'u3':
            metrics[i] += -1.0
            data = {
                "type": 'bearish',
                "value": f'volatility crossover: signal-{periods[0]}-{periods[1]}',
                "date": date,
                "index": i
            }

        elif states[i] == 'e3' and states[i-1] != 'e3':
            metrics[i] += 1.0
            data = {
                "type": 'bullish',
                "value": f'volatility crossover: {periods[1]}-{periods[0]}-signal',
                "date": date,
                "index": i
            }

        elif states[i] == 'u2' and states[i-1] == 'e1':
            metrics[i] += -0.6

        elif states[i] == 'e2' and states[i-1] == 'u1':
            metrics[i] += 0.6

        elif states[i] == 'u1' and states[i-1] == 'u3':
            metrics[i] += 0.2

        elif states[i] == 'e1' and states[i-1] == 'e3':
            metrics[i] += -0.2

        if data is not None:
            signals.append(data)

    metrics = exponential_moving_avg(metrics, 7, data_type='list')
    metrics = normalize_signals([metrics])[0]

    atr_dict['metrics'] = metrics
    atr_dict['signals'] = signals

    if plot_output and not out_suppress:
        name2 = INDEXES.get(name, name)
        title = f"{name2} - Average True Range Moving Averages"
        generate_plot(
            PlotType.DUAL_PLOTTING,
            fund['Close'],
            **{
                "y_list_2": [atr_dict['tabular'], ema_1, ema_2],
                "y1_label": 'Price', "y2_label": 'ATRs', "title": title,
                "plot_output": plot_output
            }
        )

    return atr_dict
