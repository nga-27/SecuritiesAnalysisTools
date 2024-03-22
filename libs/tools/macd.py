""" macd """
import os
from typing import Union, Tuple

import pandas as pd
import numpy as np

from libs.utils import (
    dates_extractor_list, INDEXES, TREND_COLORS, STANDARD_COLORS, PlotType, generate_plot
)
from libs.utils.progress_bar import ProgressBar, update_progress_bar
from libs.features import normalize_signals

from .moving_averages_lib.exponential_moving_avg import exponential_moving_avg


RED = TREND_COLORS.get('bad')
YELLOW = TREND_COLORS.get('hold')
GREEN = TREND_COLORS.get('good')

NORMAL = STANDARD_COLORS.get('normal')
WARNING = STANDARD_COLORS.get('warning')


def mov_avg_convergence_divergence(fund: pd.DataFrame, **kwargs) -> dict:
    """Moving Average Convergence Divergence (MACD)

    Arguments:
        fund {pd.DataFrame} -- fund historical data

    Optional Args:
        name {str} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- directory of plots (default: {''})

    Returns:
        dict -- contains all macd information in regarding macd
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar: Union[ProgressBar, None] = kwargs.get('progress_bar')
    view = kwargs.get('view', '')

    macd = generate_macd_signal(fund, plot_output=plot_output, name=name, view=view)
    update_progress_bar(progress_bar, 0.3)

    macd = get_macd_statistics(macd, progress_bar=progress_bar)
    macd = macd_metrics(fund, macd, p_bar=progress_bar,
                        name=name, plot_output=plot_output, view=view)

    macd_sig = macd['tabular']['macd']
    sig_line = macd['tabular']['signal_line']

    name3 = INDEXES.get(name, name)
    name2 = name3 + ' - MACD'
    generate_plot(
        PlotType.DUAL_PLOTTING, fund['Close'], **{
            "y_list_2": [macd_sig, sig_line], "y1_label": 'Position Price',
            "y2_label": ['MACD', 'Signal Line'], "title": name2, "plot_output": plot_output,
            "filename": os.path.join(name, view, f"macd_{name}.png")
        }
    )
    if plot_output:
        print_macd_statistics(macd)
    update_progress_bar(progress_bar, 0.3)

    macd['type'] = 'oscillator'
    macd['signals'] = get_macd_features(macd, fund)
    macd['length_of_data'] = len(macd['tabular']['macd'])
    return macd


def generate_macd_signal(fund: pd.DataFrame, **kwargs) -> dict:
    """Generate MACD Signal

    macd = ema(12) - ema(26)
    'signal' = macd(ema(9))

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        plotting {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- directory of plots (default: {''})

    Returns:
        dict -- macd data object
    """
    # pylint: disable=too-many-locals
    plotting = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view')

    macd = {}
    ema_twelve = exponential_moving_avg(fund, interval=12)
    ema_twenty_six = exponential_moving_avg(fund, interval=26)
    macd_val = []

    for i, ema_12 in enumerate(ema_twelve):
        if i < 26:
            macd_val.append(0.0)
        else:
            macd_val.append(ema_12 - ema_twenty_six[i])

    macd_sig = exponential_moving_avg(macd_val, interval=9, data_type='list')

    # Actual MACD vs. its signal line
    m_bar = []
    for i, sig in enumerate(macd_sig):
        m_bar.append(macd_val[i] - sig)

    macd['tabular'] = {'macd': macd_val, 'signal_line': macd_sig, 'bar': m_bar}
    x_dates = dates_extractor_list(fund)
    name3 = INDEXES.get(name, name)
    name2 = name3 + ' - MACD'

    generate_plot(
        PlotType.BAR_CHART, m_bar, **{
            "position": fund, "x": x_dates, "title": name2, "save_fig": True,
            "plot_output": plotting,
            "filename": os.path.join(name, view, f"macd_bar_{name}.png")
        }
    )

    return macd


def macd_metrics(position: pd.DataFrame, macd: dict, **kwargs) -> dict:
    """MACD Metrics

    Arguments:
        position {pd.DataFrame} -- fund dataset
        macd {dict} -- macd data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})
        view {str} -- directory of plots (default: {''})

    Returns:
        dict -- macd data object
    """
    # pylint: disable=too-many-locals
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('p_bar')
    view = kwargs.get('view')

    m_bar = macd['tabular']['bar']

    max_m = max(m_bar)
    min_m = min(m_bar)
    div = max_m
    if np.abs(min_m) > max_m:
        div = min_m

    macd = macd_divergences(position, macd, omit=26)

    weights = [1.0, 0.85, 0.55, 0.2]
    for mac in macd['indicators']:
        if mac['type'] == 'bearish':
            s_val = -1.0 * div / 2.0
        else:
            s_val = 1.0 * div / 2.0

        ind = mac['index']
        m_bar[ind] += s_val * weights[0]

        # Smooth the curves
        if ind - 1 >= 0:
            m_bar[ind-1] += s_val * weights[1]
        if ind + 1 < len(m_bar):
            m_bar[ind+1] += s_val * weights[1]
        if ind - 2 >= 0:
            m_bar[ind-2] += s_val * weights[2]
        if ind + 2 < len(m_bar):
            m_bar[ind+2] += s_val * weights[2]
        if ind - 3 >= 0:
            m_bar[ind-3] += s_val * weights[3]
        if ind + 3 < len(m_bar):
            m_bar[ind+3] += s_val * weights[3]

    update_progress_bar(p_bar, 0.1)
    metrics = exponential_moving_avg(m_bar, 7, data_type='list')
    norm = normalize_signals([metrics])
    metrics = norm[0]
    update_progress_bar(p_bar, 0.1)

    macd['metrics'] = metrics

    name3 = INDEXES.get(name, name)
    name2 = name3 + ' - MACD Metrics'
    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **{
            "y_list_2": metrics, "y1_label": 'Price', "y2_label": 'Metrics', "title": name2,
            "plot_output": plot_output,
            "filename": os.path.join(name, view, f"macd_metrics_{name}.png")
        }
    )

    return macd


def get_macd_features(macd: dict, position: pd.DataFrame) -> list:
    """Get MACD Features

    Arguments:
        macd {dict} -- macd data object
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of feature dictionaries
    """
    # pylint: disable=too-many-branches,too-many-statements
    features = []

    # Copy divergence features into "features" list
    for div in macd['indicators']:
        date = position.index[div['index']].strftime("%Y-%m-%d")
        data = {
            "type": div['type'],
            "value": "divergence",
            "index": div['index'],
            "date": date
        }
        features.append(data)

    # Look for zero-crossing in raw MACD signal
    macd_raw = macd['tabular']['macd']
    state = 'n'
    for i, mac in enumerate(macd_raw):
        data = None
        date = position.index[i].strftime("%Y-%m-%d")

        if state == 'n':
            if mac > 0.0:
                state = 'u1'

            elif mac < 0.0:
                state = 'e1'

        elif state == 'u1':
            if mac < 0.0:
                state = 'e1'
            else:
                state = 'u2'
                data = {
                    "type": 'bullish',
                    "value": 'zero crossing: raw MACD',
                    "index": i,
                    "date": date
                }

        elif state == 'e1':
            if mac > 0.0:
                state = 'u1'
            else:
                state = 'e2'
                data = {
                    "type": 'bearish',
                    "value": 'zero crossing: raw MACD',
                    "index": i,
                    "date": date
                }

        elif state == 'u2':
            if mac < 0.0:
                state = 'e1'
        elif state == 'e2':
            if mac > 0.0:
                state = 'u1'

        if data is not None:
            features.append(data)

    macd_bar = macd['tabular']['bar']
    state = 'n'
    for i, mac in enumerate(macd_bar):
        data = None
        date = position.index[i].strftime("%Y-%m-%d")

        if state == 'n':
            if mac > 0.0:
                state = 'u'
                data = {
                    "type": 'bullish',
                    "value": 'zero crossing: MACD & signal line',
                    "index": i,
                    "date": date
                }
            elif mac < 0.0:
                state = 'e'
                data = {
                    "type": 'bearish',
                    "value": 'zero crossing: MACD & signal line',
                    "index": i,
                    "date": date
                }

        elif state == 'u':
            if mac < 0.0:
                state = 'e'
                data = {
                    "type": 'bearish',
                    "value": 'zero crossing: MACD & signal line',
                    "index": i,
                    "date": date
                }

        elif state == 'e':
            if mac < 0.0:
                state = 'u'
                data = {
                    "type": 'bullish',
                    "value": 'zero crossing: MACD & signal line',
                    "index": i,
                    "date": date
                }

        if data is not None:
            features.append(data)
    return features


def get_macd_statistics(macd: dict, **kwargs) -> dict:
    """Get MACD Statistics

    Arguments:
        macd {dict} -- macd data object

    Optional Args:
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- macd data object
    """
    progress_bar = kwargs.get('progress_bar')

    macd_sig = macd['tabular']['macd']
    macd['state'] = get_macd_state(macd_sig)

    macd['period_value'] = get_macd_value(macd_sig, value_type='current')
    macd['group_value'] = get_macd_value(macd_sig, value_type='group')
    update_progress_bar(progress_bar, 0.1)

    macd['current_trend'] = get_macd_trend(macd_sig, trend_type='current')
    macd['group_trend'] = get_macd_trend(macd_sig, trend_type='group')

    macd['change'] = get_macd_value(macd_sig, value_type='change')
    update_progress_bar(progress_bar, 0.1)
    return macd


def print_macd_statistics(macd: dict):
    """Print MACD Statistics

    Arguments:
        macd {dict} -- macd data object
    """
    # pylint: disable=too-many-branches
    print("\r\nMACD Statistics:")
    if np.abs(macd['period_value']) < 7.5:
        color = YELLOW
    elif macd['period_value'] < 0.0:
        color = RED
    else:
        color = GREEN
    print(
        f"\r\nPeriod: {color}{np.round(macd['period_value'], 3)}%{NORMAL} of total time window")

    if np.abs(macd['group_value']) < 25.0:
        color = YELLOW
    elif macd['group_value'] < 0.0:
        color = RED
    else:
        color = GREEN
    print(
        f"Group: {color}{np.round(macd['group_value'], 3)}%{NORMAL} of the current +/- grouping")

    if macd['current_trend'] == 'falling':
        color = RED
    else:
        color = GREEN
    print(f"Current Trend: {color}{macd['current_trend']}{NORMAL}")

    if macd['group_trend'] == 'falling':
        color = RED
    else:
        color = GREEN
    print(
        f"Group Trend: {color}{macd['group_trend']}{NORMAL} (in relation to rest of +/- grouping)")

    if np.abs(macd['change']) < 25.0:
        color = YELLOW
    elif macd['change'] < 0.0:
        color = RED
    else:
        color = GREEN

    print(
        f"Change: {color}{np.round(macd['change'], 3)}%{NORMAL} from moving average signal")

    color = macd['state'][1]
    print(f"Overall MACD State: {color}{macd['state'][0]}{NORMAL}\r\n")


##########################################

def get_macd_state(macd: list) -> Tuple[str, Union[str, None]]:
    """
    states: 'strongly', 'weakly', 'crossover' + bear/bullish
    """
    cross_str, color = has_crossover(macd)
    if cross_str is not None:
        return cross_str, color

    intensity = get_macd_value(macd, value_type='group')
    factor = get_group_duration_factor(macd, len(macd)-1, f_type='state')
    intensity = intensity / factor
    if np.abs(intensity) > 70.0:
        if intensity > 0.0:
            return 'strongly_bullish', GREEN
        return 'strongly_bearish', RED

    if intensity > 0.0:
        return 'weakly_bullish', YELLOW
    return 'weakly_bearish', YELLOW


def has_crossover(signal: list, interval: int = 3) -> Tuple[Union[str, None], Union[str, None]]:
    """ Check if a 0 crossing occurred in last 'interval' periods """
    # pylint: disable=chained-comparison
    if (signal[-1] > 0.0) and (signal[-1-interval] < 0.0):
        return 'crossover_bullish', GREEN
    if (signal[-1] < 0.0) and (signal[-1-interval] > 0.0):
        return 'crossover_bearish', RED
    return None, None


def get_group_duration_factor(signal: list, index: int, f_type='signal') -> float:
    """ normalization to crossovers of different sizes """
    if index - 2 > 0:
        index -= 2
    else:
        return 1.25

    data_range_1 = get_group_range(signal, index)
    if data_range_1[0] - 2 > 0:
        # 'start' variable
        data_range_2 = get_group_range(signal, data_range_1[0]-2)
    else:
        return 1.25

    d_max = np.max([data_range_1[2], data_range_2[2]])
    if f_type == 'signal':
        factor = 1.25 - (data_range_1[2] / d_max) * 0.25
    elif f_type == 'score':
        factor = 1.1 - (data_range_1[2] / d_max) * 0.1
    elif f_type == 'state':
        factor = 1.5 - (data_range_1[2] / d_max) * 0.5
    else:
        return 1.0
    return factor


def get_group_max(signal: list, index=-1) -> float:
    """ Get group max of a specified range """
    if index == -1:
        index = len(signal)-1
    start, end, _ = get_group_range(signal, index)
    macd_max = np.max(np.abs(signal[start:end+1]))
    return macd_max


def get_macd_value(macd: list, value_type='current', index=-1) -> Union[float, None]:
    """ Get MACD value to display in single function printout """
    if value_type == 'current':
        macd_max = np.max(np.abs(macd))
        return macd[-1] / macd_max * 100.0

    if value_type == 'group':
        macd_max = get_group_max(macd, index=index)
        if macd_max == 0.0:
            return 0.0
        return macd[index] / np.abs(macd_max) * 100.0

    if value_type == 'change':
        macd_ema = exponential_moving_avg(macd, interval=3, data_type='list')
        macd_max = get_group_max(macd)
        if macd_max == 0.0:
            return 0.0
        val = (macd[-1] - macd_ema[-1]) / \
            macd_max * 100.0
        return val
    return None


def get_group_range(signal: list, index: int) -> Tuple[int, int, int]:
    """ [start_index, end_index] """
    if signal[index] > 0.0:
        state = 1
    else:
        state = 0

    start = index
    while start >= 0:
        if state == 1:
            if signal[start] < 0.0:
                start += 1
                break
        else:
            if signal[start] > 0.0:
                start += 1
                break
        start -= 1

    if start == -1:
        start = 0

    end = index
    while end < len(signal):
        if state == 1:
            if signal[end] < 0.0:
                end -= 1
                break
        else:
            if signal[end] > 0.0:
                end -= 1
                break
        end += 1
    return [start, end, (end-start+1)]


def get_macd_trend(macd: list, trend_type: str = 'current') -> Union[str, None]:
    """ Get MACD Trend as a simple point-slope form """
    # pylint: disable=too-many-return-statements,too-many-branches
    if trend_type == 'current':
        if macd[len(macd)-1] > macd[len(macd)-2]:
            return 'rising'
        return 'falling'

    if trend_type == 'group':
        if macd[len(macd)-1] > 0.0:
            state = 1
        else:
            state = 0

        if state == 1:
            i = len(macd)-2
            group_size = 0
            while (i > 0) and (state == 1):
                if macd[i] > 0.0:
                    i -= 1
                    group_size += 1
                else:
                    state = 0

            m_ema = exponential_moving_avg(
                macd[i:len(macd)], interval=3, data_type='list')
            if len(m_ema) > 0:
                if macd[len(macd)-1] > m_ema[len(m_ema)-1]:
                    return 'rising'
                return 'falling'

        else:
            i = len(macd)-2
            group_size = 0
            while (i > 0) and (state == 1):
                if macd[i] <= 0.0:
                    i -= 1
                    group_size += 1
                else:
                    state = 0

            m_ema = exponential_moving_avg(
                macd[i:len(macd)], interval=3, data_type='list')
            if len(m_ema) > 0:
                if macd[len(macd)-1] > m_ema[len(m_ema)-1]:
                    return 'rising'
                return 'falling'

    else:
        print(
            f"{WARNING}WARNING - no valid 'trend_type' provided in 'get_macd_trend'.{NORMAL}")
        return None
    # Final catch-all of states, neither rising nor falling, nor error
    return None


def macd_divergences(position: pd.DataFrame, macd: dict, **kwargs) -> dict:
    """MACD Divergences

    Discover any MACD divergences with price

    Arguments:
        position {pd.DataFrame} -- fund dataset
        macd {dict} -- macd data object

    Optional Args:
        omit {int} -- starting index, so omit up to index (default: {0})

    Returns:
        dict -- macd data object
    """
    # pylint: disable=too-many-branches,too-many-statements
    omit = kwargs.get('omit', 0)

    macd['indicators'] = []
    state = 'n'
    prices = [0.0, 0.0]
    ms_list = [0.0, 0.0]
    closes = position['Close']
    md_list = macd['tabular']['macd']

    for i in range(omit, len(md_list)):
        # Start with bullish divergences
        if (state == 'n') and (md_list[i] < 0.0):
            state = 'u1'
            ms_list[0] = md_list[i]

        elif state == 'u1':
            if md_list[i] < ms_list[0]:
                ms_list[0] = md_list[i]
            else:
                prices[0] = closes[i-1]
                ms_list[1] = md_list[i]
                state = 'u2'

        elif state == 'u2':
            if md_list[i] > ms_list[1]:
                if md_list[i] > 0.0:
                    state = 'e1'
                    ms_list[0] = md_list[i]
                else:
                    ms_list[1] = md_list[i]
            else:
                state = 'u3'

        elif state == 'u3':
            if md_list[i] <= ms_list[1]:
                ms_list[1] = md_list[i]
                if md_list[i] <= ms_list[0]:
                    state = 'u1'
            else:
                state = 'u4'
                prices[1] = closes[i-1]

        elif state == 'u4':
            if md_list[i] >= ms_list[1]:
                if (prices[1] < prices[0]) and (ms_list[0] < ms_list[1]):
                    macd['indicators'].append(
                        {'index': i, 'type': 'bullish', 'style': 'divergence'})
                    state = 'n'
                else:
                    # Not truly divergence
                    state = 'u1'
            else:
                state = 'u3'

        # Start with bearish divergences
        if (state == 'n') and (md_list[i] > 0.0):
            state = 'e1'
            ms_list[0] = md_list[i]

        elif state == 'e1':
            if md_list[i] > ms_list[0]:
                ms_list[0] = md_list[i]
            else:
                prices[0] = closes[i-1]
                ms_list[1] = md_list[i]
                state = 'e2'

        elif state == 'e2':
            if md_list[i] < ms_list[1]:
                if md_list[i] < 0.0:
                    state = 'u1'
                    ms_list[0] = md_list[i]
                else:
                    ms_list[1] = md_list[i]
            else:
                state = 'e3'

        elif state == 'e3':
            if md_list[i] >= ms_list[1]:
                ms_list[1] = md_list[i]
                if md_list[i] >= ms_list[0]:
                    state = 'e1'
            else:
                state = 'e4'
                prices[1] = closes[i-1]

        elif state == 'e4':
            if md_list[i] <= ms_list[1]:
                if (prices[1] > prices[0]) and (ms_list[0] < ms_list[1]):
                    macd['indicators'].append(
                        {'index': i, 'type': 'bearish', 'style': 'divergence'})
                    state = 'n'
                else:
                    # Not truly divergence
                    state = 'e1'
            else:
                state = 'e3'
    return macd
