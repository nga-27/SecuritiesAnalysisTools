""" ultimate oscillator """
import os
from typing import Union

import pandas as pd
import numpy as np

from libs.utils import date_extractor, INDEXES, PlotType, generate_plot
from libs.features import normalize_signals

from .math_functions import lower_low, higher_high, bull_bear_th
from .moving_average import exponential_moving_avg


def ultimate_oscillator(position: pd.DataFrame, config: Union[list, None] = None, **kwargs) -> dict:
    """Ultimate Oscillator

    Arguments:
        position {pd.DataFrame} -- dataset

    Keyword Arguments:
        config {list} -- time period window (default: {[7, 14, 28]})

    Optional Args:
        plot_output {bool} -- (default: {True})
        out_suppress {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- ultimate oscillator object
    """
    if not config:
        config = [7, 14, 28]
    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')
    view = kwargs.get('view', '')

    ultimate = {}
    ult_osc = generate_ultimate_osc_signal(position, config=config, p_bar=p_bar)
    ultimate['tabular'] = ult_osc

    ultimate = find_ult_osc_features(position, ultimate, p_bar=p_bar)

    ultimate = ult_osc_output(
        ultimate, len(position['Close']), p_bar=p_bar)

    ultimate = ultimate_osc_metrics(
        position,
        ultimate,
        plot_output=plot_output,
        out_suppress=out_suppress,
        name=name,
        p_bar=p_bar,
        view=view)

    if not out_suppress:
        name3 = INDEXES.get(name, name)
        name2 = name3 + ' - Ultimate Oscillator'

        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **{
                "y_list_2": ult_osc, "y1_label": 'Position Price',
                "y2_label": 'Ultimate Oscillator',
                "title": name2, "plot_output": plot_output, "subplot": True,
                "filename": os.path.join(name, view, f"ultimate_osc_raw_{name}.png")
            }
        )
        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **{
                "y_list_2": ultimate['plots'], "y1_label": 'Position Price',
                "y2_label": 'Buy-Sell Signal', "title": name2, "plot_output": plot_output,
                "filename": os.path.join(name, view, f"ultimate_osc_raw_{name}.png")
            }
        )

    ultimate['type'] = 'oscillator'
    ultimate['length_of_data'] = len(ultimate['tabular'])
    ultimate['signals'] = ultimate_osc_signals(
        ultimate['bullish'], ultimate['bearish'])

    return ultimate


def generate_ultimate_osc_signal(position: pd.DataFrame,
                                 config: Union[list, None] = None, **kwargs) -> list:
    """Generate Ultimate Oscillator Signal

    Arguments:
        position {pd.DataFrame}

    Keyword Arguments:
        config {list} -- (default: {[7, 14, 28]})

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- signal
    """
    # pylint: disable=too-many-locals
    if not config:
        config = [7, 14, 28]

    p_bar = kwargs.get('p_bar')
    tot_len = len(position['Close'])
    short = config[0]
    medium = config[1]
    long = config[2]

    bp_val = [0.0] * tot_len
    tr_val = [0.0] * tot_len
    u_short = [0.0] * tot_len
    u_med = [0.0] * tot_len
    u_long = [0.0] * tot_len
    ult_osc = [50.0] * tot_len

    # Generate the ultimate oscillator values
    for i in range(1, tot_len):
        low = np.min([position['Low'][i], position['Close'][i-1]])
        high = np.max([position['High'][i], position['Close'][i-1]])
        bp_val[i] = np.round(position['Close'][i] - low, 6)
        tr_val[i] = np.round(high - low, 6)

        if i >= short-1:
            sh_bp = sum(bp_val[i-short: i+1])
            sh_tr = sum(tr_val[i-short: i+1])
            if sh_tr != 0.0:
                u_short[i] = np.round(sh_bp / sh_tr, 6)

        if i >= medium-1:
            sh_bp = sum(bp_val[i-medium: i+1])
            sh_tr = sum(tr_val[i-medium: i+1])
            if sh_tr != 0.0:
                u_med[i] = np.round(sh_bp / sh_tr, 6)

        if i >= long-1:
            sh_bp = sum(bp_val[i-long: i+1])
            sh_tr = sum(tr_val[i-long: i+1])
            if sh_tr != 0.0:
                u_long[i] = np.round(sh_bp / sh_tr, 6)
            ult_osc[i] = \
                np.round(
                    100.0 * ((4.0 * u_short[i]) + (2.0 * u_med[i]) + u_long[i]) / 7.0, 6)

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    return ult_osc


def find_ult_osc_features(position: pd.DataFrame, ultimate: dict, **kwargs) -> list:
    """Find Ultimate Oscillator Features

    Arguments:
        position {pd.DataFrame} -- dataset
        ultimate {dict} -- ultimate osc data object

    Optional Args:
        thresh_low {int} -- oversold signal threshold (default: {30})
        thresh_high {int} -- overbought signal threshold (default: {70})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- ultimate osc data object
    """
    # pylint: disable=too-many-locals,too-many-statements,too-many-branches
    p_bar = kwargs.get('p_bar')
    low_th = kwargs.get('thresh_low', 30)
    high_th = kwargs.get('thresh_high', 70)

    ult_osc = ultimate['tabular']

    trigger = []
    marker_val = 0.0
    marker_ind = 0

    for i, close in enumerate(position['Close']):
        # Find bullish signal
        if ult_osc[i] < low_th:
            ult1 = ult_osc[i]
            marker_val = close
            marker_ind = i
            lows = lower_low(position['Close'], marker_val, marker_ind)

            if len(lows) != 0:
                ult2 = ult_osc[lows[-1][1]]

                if ult2 > ult1:
                    start_ind = lows[-1][1]
                    interval = np.max(ult_osc[i:start_ind+1])
                    start_ind = bull_bear_th(
                        ult_osc, start_ind, interval, bull_bear='bull')

                    if start_ind is not None:
                        trigger.append([
                            "BULLISH",
                            date_extractor(
                                position.index[start_ind], _format='str'),
                            position['Close'][start_ind],
                            start_ind,
                            "divergence (original)"
                        ])

        # Find bearish signal
        if ult_osc[i] > high_th:
            ult1 = ult_osc[i]
            marker_val = position['Close'][i]
            marker_ind = i
            highs = higher_high(position['Close'], marker_val, marker_ind)

            if len(highs) != 0:
                ult2 = ult_osc[highs[-1][1]]

                if ult2 < ult1:
                    start_ind = highs[-1][1]
                    interval = np.min(ult_osc[i:start_ind+1])
                    start_ind = bull_bear_th(
                        ult_osc, start_ind, interval, bull_bear='bear')

                    if start_ind is not None:
                        trigger.append([
                            "BEARISH",
                            date_extractor(
                                position.index[start_ind], _format='str'),
                            position['Close'][start_ind],
                            start_ind,
                            "divergence (original)"
                        ])

    if p_bar is not None:
        p_bar.uptick(increment=0.3)

    state = 'n'
    prices = [0.0, 0.0]
    ults = [0.0, 0.0, 0.0]

    for i, ult in enumerate(ult_osc):

        # Find bullish divergence and breakout
        if (state == 'n') and (ult <= low_th):
            state = 'u1'
            ults[0] = ult

        elif state == 'u1':
            if ult < ults[0]:
                ults[0] = ult
            else:
                prices[0] = position['Close'][i-1]
                state = 'u2'

        elif (state == 'u2') and (ult > low_th):
            state = 'u3'
            ults[1] = ult

        elif state == 'u3':
            if ult > ults[1]:
                ults[1] = ult
            else:
                # we think we've found a divergent high
                state = 'u4'
                ults[2] = ult

        elif state == 'u4':
            if ults[2] >= ult:
                ults[2] = ult
            else:
                # We think we've found the bullish 2nd low
                prices[1] = position['Close'][i-1]
                state = 'u5'

        elif state == 'u5':
            if ult > ults[1]:
                if prices[0] > prices[1]:
                    # Bullish breakout!
                    if start_ind:
                        trigger.append([
                            "BULLISH",
                            date_extractor(position.index[start_ind], _format='str'),
                            position['Close'][start_ind],
                            start_ind,
                            "divergence"
                        ])
                    state = 'n'
                else:
                    # False breakout, see if this is the new max:
                    state = 'u3'
                    ults[1] = ult

            elif ult < ults[2]:
                # There may have been a false signal
                ults[2] = ult
                state = 'u4'

        # Find bullish divergence and breakout
        if (state == 'n') and (ult >= high_th):
            state = 'e1'
            ults[0] = ult

        elif state == 'e1':
            if ult > ults[0]:
                ults[0] = ult
            else:
                prices[0] = position['Close'][i-1]
                state = 'e2'

        elif (state == 'e2') and (ult < high_th):
            state = 'e3'
            ults[1] = ult

        elif state == 'e3':
            if ult < ults[1]:
                ults[1] = ult
            else:
                # we think we've found a divergent low
                state = 'e4'
                ults[2] = ult

        elif state == 'e4':
            if ults[2] <= ult:
                ults[2] = ult
            else:
                # We think we've found the bullish 2nd high
                prices[1] = position['Close'][i-1]
                state = 'e5'

        elif state == 'e5':
            if ult < ults[1]:
                if prices[0] < prices[1]:
                    # Bullish breakout!
                    if start_ind:
                        trigger.append([
                            "BEARISH",
                            date_extractor(position.index[start_ind], _format='str'),
                            position['Close'][start_ind],
                            start_ind,
                            "divergence"
                        ])
                    state = 'n'
                else:
                    # False breakout, see if this is the new max:
                    state = 'e3'
                    ults[1] = ult

            elif ult > ults[2]:
                # There may have been a false signal
                ults[2] = ult
                state = 'e4'

        elif ult >= high_th:
            state = 'e1'
            ults[0] = ult

        elif ult <= low_th:
            state = 'u1'
            ults[0] = ult

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    ultimate['indicator'] = trigger

    return ultimate


def ult_osc_output(ultimate: dict, len_of_position: int, **kwargs) -> list:
    """Ultimate Oscillator Output

    Simplifies signals to easy to view plot and dictionary

    Arguments:
        ultimate {dict} -- ultimate oscillator data object
        len_of_position {int} -- length of fund dataset (without passing it)

    Optional Args:
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- plot (list), easy signal to plot on top of a position's price plot;
                ultimate (dict), dictionary of specific information represented by 'plot' signal
    """
    p_bar = kwargs.get('p_bar')

    ultimate['bullish'] = []
    ultimate['bearish'] = []

    trigger = ultimate['indicator']

    simplified = []
    plots = [0.0] * len_of_position
    present = False

    for trig in trigger:
        for _, simple in enumerate(simplified):
            if simple[3] == trig[3]:
                present = True

        if not present:
            simplified.append(trig)

            if trig[0] == "BEARISH":
                plots[trig[3]] = -1.0
                ultimate['bearish'].append(
                    [trig[1], trig[2], trig[3], trig[4]])

            else:
                plots[trig[3]] = 1.0
                ultimate['bullish'].append(
                    [trig[1], trig[2], trig[3], trig[4]])

        present = False

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    ultimate['plots'] = plots

    return ultimate


def ultimate_osc_metrics(position: pd.DataFrame, ultimate: dict, **kwargs) -> dict:
    """Ultimate Oscillator Metrics

    Arguments:
        position {pd.DataFrame} -- fund dataset
        ultimate {dict} -- ultimate osc data object

    Optional Args:
        p_bar {ProgressBar} -- (default: {None})
        plot_output {bool} -- (default: {True})
        out_suppress {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})

    Returns:
        dict -- ultimate osc data object
    """
    # pylint: disable=too-many-locals
    p_bar = kwargs.get('p_bar')
    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')

    ults = ultimate['plots']

    # Take indicator set: weight, filter, normalize
    weights = [1.0, 0.9, 0.75, 0.45]
    state2 = [0.0] * len(ults)

    for ind, s_val in enumerate(ults):
        if s_val != 0.0:
            state2[ind] += s_val

            # Smooth the curves
            if ind - 1 >= 0:
                state2[ind-1] += s_val * weights[1]
            if ind + 1 < len(ults):
                state2[ind+1] += s_val * weights[1]
            if ind - 2 >= 0:
                state2[ind-2] += s_val * weights[2]
            if ind + 2 < len(ults):
                state2[ind+2] += s_val * weights[2]
            if ind - 3 >= 0:
                state2[ind-3] += s_val * weights[3]
            if ind + 3 < len(ults):
                state2[ind+3] += s_val * weights[3]

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    metrics = exponential_moving_avg(state2, 7, data_type='list')
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    norm = normalize_signals([metrics])
    metrics = norm[0]

    if not out_suppress:
        name3 = INDEXES.get(name, name)
        name2 = name3 + ' - Ultimate Oscillator Metrics'

        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **{
                "y_list_2": metrics, "y1_label": 'Price', "y2_label": 'Metrics', "title": name2,
                "plot_output": plot_output,
                "filename": os.path.join(name, view, f"ultimate_osc_metrics_{name}.png")
            }
        )

    ultimate['metrics'] = metrics

    return ultimate


def ultimate_osc_signals(bull_list: list, bear_list: list) -> list:
    """Ultimate Oscillator Signals

    Format all ultimate_osc signals into a single list

    Arguments:
        bull_list {list} -- list of bullish signals
        bear_list {list} -- list of bearish signals

    Returns:
        list -- list of ultimate_osc signals
    """
    signals_of_note = []
    for sig in bull_list:
        data = {
            "type": 'bullish',
            "value": sig[3],
            "index": sig[2],
            "date": sig[0]
        }
        signals_of_note.append(data)

    for sig in bear_list:
        data = {
            "type": 'bearish',
            "value": sig[3],
            "index": sig[2],
            "date": sig[0]
        }
        signals_of_note.append(data)

    return signals_of_note
