""" RSI """
import os
import math
from typing import Union

import pandas as pd
import numpy as np

from libs.utils import date_extractor, INDEXES, generate_plot, PlotType
from libs.features import normalize_signals

from .trends import auto_trend
from .moving_average import exponential_moving_avg
from .trends import get_trend_lines_regression


def relative_strength_indicator_rsi(position: pd.DataFrame, **kwargs) -> dict:
    """Relative Strength Indicator

    Arguments:
        position {pd.DataFrame} -- list of y-value datasets to be plotted (multiple)

    Optional Args:
        name {str} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        period {int} -- size of relative_strength_indicator_rsi indicator (default: {14})
        out_suppress {bool} -- output plot/prints are suppressed (default: {True})
        progress_bar {ProgressBar} -- (default: {None})
        overbought {float} -- threshold to trigger overbought/sell condition (default: {70.0})
        oversold {float} -- threshold to trigger oversold/buy condition (default: {30.0})
        auto_trend {bool} -- True calculates basic trend, applies to thresholds (default: {True})
        view {str} -- (default: {''})
        trendlines {bool} -- (default: {False})

    Returns:
        dict -- contains all rsi information
    """
    # pylint: disable=too-many-locals
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    period = kwargs.get('period', 14)
    out_suppress = kwargs.get('out_suppress', True)
    progress_bar = kwargs.get('progress_bar', None)
    overbought = kwargs.get('overbought', 70.0)
    oversold = kwargs.get('oversold', 30.0)
    use_auto_trend = kwargs.get('auto_trend', True)
    view = kwargs.get('view', '')
    has_trend_lines = kwargs.get('trendlines', False)

    rsi_data = {}
    rsi = generate_rsi_signal(position, period=period, p_bar=progress_bar)
    rsi_data['tabular'] = rsi

    slope_trend = []
    if use_auto_trend:
        slope_trend = auto_trend(position['Close'], periods=[period*3, period*5.5, period*8],
            weights=[0.45, 0.33, 0.22], normalize=True)

    over_thresholds = over_threshold_lists(
        overbought, oversold, len(position['Close']), slope_list=slope_trend)
    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    rsi_data['thresholds'] = over_thresholds

    # Determine indicators, swing rejection and divergences
    rsi_data = determine_rsi_swing_rejection(
        position, rsi_data, p_bar=progress_bar)

    rsi_data = rsi_divergence(position, rsi_data, plot_output=plot_output, p_bar=progress_bar)

    # Determine metrics, primarily using both indicators
    rsi_data = rsi_metrics(rsi_data, p_bar=progress_bar)

    main_plots = [rsi, over_thresholds['overbought'],
                  over_thresholds['oversold']]

    if not out_suppress:
        name3 = INDEXES.get(name, name)
        name2 = name3 + ' - relative_strength_indicator_rsi'

        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **dict(
                y_list_2=main_plots, y1_label='Position Price',
                y2_label='relative_strength_indicator_rsi', title=name2, plot_output=plot_output,
                filename=os.path.join(name, view, f"RSI_standard_{name}.png")
            )
        )
        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **dict(
                y_list_2=main_plots, y1_label='Position Price',
                y2_label='relative_strength_indicator_rsi Metrics', title=name2,
                plot_output=plot_output,
                filename=os.path.join(name, view, f"RSI_indicator_{name}.png")
            )
        )

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    if has_trend_lines:
        end = len(rsi)
        rsi_trend = rsi[end-100: end]
        get_trend_lines_regression(rsi_trend, plot_output=True,
            indicator='relative_strength_indicator_rsi')

    rsi_data['type'] = 'oscillator'
    rsi_data['length_of_data'] = len(rsi)
    rsi_data['signals'] = rsi_signals(rsi_data['bullish'], rsi_data['bearish'])

    return rsi_data


def generate_rsi_signal(position: pd.DataFrame, **kwargs) -> list:
    """Generate relative_strength_indicator_rsi Signal

    Arguments:
        position {pd.DataFrame}

    Keyword Arguments:
        period {int} -- (default: {14})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- relative_strength_indicator_rsi signal
    """
    # pylint: disable=too-many-branches
    period = kwargs.get('period', 14)
    p_bar = kwargs.get('p_bar')

    change = []
    change.append(0.0)
    for i in range(1, len(position['Close'])):
        per = (position['Close'][i] - position['Close']
               [i-1]) / position['Close'][i-1] * 100.0
        change.append(np.round(per, 6))

    if p_bar is not None:
        p_bar.uptick(increment=0.15)

    relative_strength_indicator_rsi_list = []
    # gains, losses, rs
    rsi_list = []

    for i in range(0, period):
        relative_strength_indicator_rsi_list.append(50.0)
        rsi_list.append([0.0, 0.0, 1.0])

    # Calculate RS for all future points
    for i in range(period, len(change)):
        pos = 0.0
        neg = 0.0
        for j in range(i-period, i):
            if change[j] > 0.0:
                pos += change[j]
            else:
                neg += np.abs(change[j])

        if i == period:
            if neg == 0.0:
                rsi_val = float('inf')
            else:
                rsi_val = np.round(pos / neg, 6)
            rsi_list.append([
                np.round(pos/float(period), 6), np.round(neg/float(period), 6), rsi_val
            ])

        else:
            if change[i] > 0.0:
                if rsi_list[i-1][1] == 0.0:
                    rsi_val = float('inf')
                else:
                    rsi_val = (((rsi_list[i-1][0] * float(period-1)) + change[i]) / \
                        float(period)) / \
                         (((rsi_list[i-1][1] * float(period-1)) + 0.0) / float(period))
            else:
                if rsi_list[i-1][1] == 0.0:
                    rsi_val = float('inf')
                else:
                    rsi_val = (((rsi_list[i-1][0] * float(period-1)) + 0.00) / float(period)) / \
                        (((rsi_list[i-1][1] * float(period-1)) +
                          np.abs(change[i])) / float(period))

            rsi_list.append([np.round(pos/float(period), 6),
                       np.round(neg/float(period), 6), rsi_val])

        rsi = 100.0 - (100.0 / (1.0 + rsi_list[i][2]))
        relative_strength_indicator_rsi_list.append(np.round(rsi, 6))

    if p_bar is not None:
        p_bar.uptick(increment=0.15)

    return relative_strength_indicator_rsi_list


def determine_rsi_swing_rejection(position: pd.DataFrame, rsi_data: dict, **kwargs) -> dict:
    """ Find bullish / bearish and relative_strength_indicator_rsi indicators

    1. go beyond threshold
    2. go back within thresholds
    3. have local minima/maxima inside thresholds
    4. exceed max/min (bull/bear) of previous maxima/minima

    Arguments:
        position {pd.DataFrame} -- fund data
        rsi_signal {list} -- pure relative_strength_indicator_rsi signal
        rsi_data {dict} -- relative_strength_indicator_rsi data object

    Optional Args:
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- rsi data object
    """
    # pylint: disable=too-many-statements,too-many-branches
    p_bar = kwargs.get('p_bar', None)

    thresholds = rsi_data['thresholds']
    rsi_signal = rsi_data['tabular']

    if thresholds is None:
        thresholds = {}
        thresholds['oversold'] = [30.0] * len(position['Close'])
        thresholds['overbought'] = [70.0] * len(position['Close'])

    low_th = thresholds['oversold']
    high_th = thresholds['overbought']

    rsi_data['bullish'] = []
    rsi_data['bearish'] = []
    indicator = []

    increment = 0.2 / float(len(rsi_signal))

    state = 0
    minima = 0.0
    maxima = 0.0
    for i, sig in enumerate(rsi_signal):
        if (state == 0) and (sig <= low_th[i]):
            # Start of a bullish signal
            state = 1
            indicator.append(0.0)

        elif (state == 1) and (sig > low_th[i]):
            state = 2
            maxima = sig
            indicator.append(0.0)

        elif state == 2:
            if sig >= maxima:
                if sig >= high_th[i]:
                    state = 5
                else:
                    maxima = sig
            else:
                minima = sig
                state = 3
            indicator.append(0.0)

        elif state == 3:
            if sig <= low_th[i]:
                # Failed attempted breakout
                state = 1
            elif rsi_signal[i] <= minima:
                minima = sig
            else:
                state = 4
            indicator.append(0.0)

        elif state == 4:
            if sig > maxima:
                # Have found a bullish breakout!
                rsi_data['bullish'].append([
                    date_extractor(position.index[i], _format='str'),
                    position['Close'][i],
                    i,
                    "swing rejection"
                ])
                state = 0
                minima = 0.0
                maxima = 0.0
                indicator.append(1.0)
            else:
                if sig <= low_th[i]:
                    state = 1
                indicator.append(0.0)

        elif (state == 0) and (sig >= high_th[i]):
            state = 5
            indicator.append(0.0)

        elif (state == 5) and (sig < high_th[i]):
            state = 6
            minima = sig
            indicator.append(0.0)

        elif state == 6:
            if sig <= minima:
                if sig <= low_th[i]:
                    state = 1
                else:
                    minima = sig
            else:
                maxima = sig
                state = 7
            indicator.append(0.0)

        elif state == 7:
            if sig >= high_th[i]:
                # Failed attempted breakout
                state = 5
            elif sig >= maxima:
                maxima = sig
            else:
                state = 8
            indicator.append(0.0)

        elif state == 8:
            if sig < minima:
                rsi_data['bearish'].append([
                    date_extractor(position.index[i], _format='str'),
                    position['Close'][i],
                    i,
                    "swing rejection"
                ])
                state = 0
                minima = 0.0
                maxima = 0.0
                indicator.append(-1.0)
            else:
                if sig >= high_th[i]:
                    state = 5
                indicator.append(0.0)

        else:
            indicator.append(0.0)

        if p_bar is not None:
            p_bar.uptick(increment=increment)

    rsi_data['indicator'] = indicator

    return rsi_data


def over_threshold_lists(overbought: float,
                         oversold: float,
                         fund_length: int,
                         slope_list: Union[list, None] = None) -> dict:
    """Over Threshold Lists

    Arguments:
        overbought {float} -- default value of overbought (default: {70.0})
        oversold {float} -- default value of oversold (default: {30.0})
        fund_length {int} -- length of fund

    Keyword Arguments:
        slope_list {list} -- generalized trendline of a given region (default: {[]})

    Returns:
        dict -- [description]
    """
    if not slope_list:
        slope_list = []
    over_bought_list = []
    over_sold_list = []

    if len(slope_list) == 0:
        over_bought_list = [overbought] * len(fund_length)
        over_sold_list = [oversold] * len(fund_length)

    else:
        for slope in slope_list:
            if slope > 0.1:
                # 'Up' trend, oversold rises proportionally
                over_bought_list.append(overbought)
                sl_exp = (slope - 0.1) * -15.0
                sld = (10.0 - (10.0 * math.exp(sl_exp))) + oversold
                over_sold_list.append(sld)

            elif slope < -0.1:
                # 'Down' trend, overbought drops proportionally
                sl_exp = (slope + 0.1) * 15.0
                bot = overbought - (10.0 - (10.0 * math.exp(sl_exp)))
                over_bought_list.append(bot)
                over_sold_list.append(oversold)

            else:
                over_bought_list.append(overbought)
                over_sold_list.append(oversold)

    over_th = {"overbought": over_bought_list, "oversold": over_sold_list}
    return over_th


def rsi_divergence(position: pd.DataFrame, rsi_data: dict, **kwargs) -> dict:
    """relative_strength_indicator_rsi Divergence:

    1. Cross outside threshold at Price A
    2. Cross inside threshold
    3. Cross outside threshold at Price B
    4. Exit [inside] threshold, where Price B is more extreme than A

    Arguments:
        position {pd.DataFrame} -- dataset
        rsi_data {dict} -- rsi data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- rsi data object
    """
    # pylint: disable=too-many-statements,too-many-branches,too-many-locals
    plot_output = kwargs.get('plot_output', True)
    p_bar = kwargs.get('p_bar')

    signal = rsi_data['tabular']
    ovb_th = rsi_data['thresholds']['overbought']
    ovs_th = rsi_data['thresholds']['oversold']

    divs = [0.0] * len(signal)

    state = 'n'
    maxima = 0.0
    minima = 0.0
    prices = [0.0, 0.0]
    rsi_vals = [0.0, 0.0]

    for i, sig in enumerate(signal):
        # Start with bullish divergence
        if (state == 'n') and (sig <= ovs_th[i]):
            state = 'u1'
            rsi_vals[0] = sig

        elif state == 'u1':
            if sig <= rsi_vals[0]:
                rsi_vals[0] = sig
                prices[0] = position['Close'][i]
            else:
                state = 'u2'
                maxima = sig

        elif state == 'u2':
            if sig >= maxima:
                if sig >= ovb_th[i]:
                    state = 'e1'
                    rsi_vals[0] = sig
                else:
                    maxima = sig
            else:
                state = 'u3'
                rsi_vals[1] = sig

        elif state == 'u3':
            if sig <= rsi_vals[1]:
                prices[1] = position['Close'][i]
                rsi_vals[1] = sig
            else:
                if rsi_vals[1] <= ovs_th[i]:
                    if (prices[1] < prices[0]) and (rsi_vals[0] < rsi_vals[1]):
                        # Bullish divergence!
                        divs[i] = 1.0
                        rsi_data['bullish'].append([
                            date_extractor(position.index[i], _format='str'),
                            position['Close'][i],
                            i,
                            "divergence"
                        ])
                        state = 'n'
                    else:
                        state = 'n'
                else:
                    state = 'n'

        # Start with bearish divergence
        elif (state == 'n') and (sig >= ovb_th[i]):
            state = 'e1'
            rsi_vals[0] = sig

        elif state == 'e1':
            if sig >= rsi_vals[0]:
                rsi_vals[0] = sig
                prices[0] = position['Close'][i]
            else:
                state = 'e2'
                minima = sig

        elif state == 'e2':
            if sig <= minima:
                if sig <= ovs_th[i]:
                    state = 'u1'
                    rsi_vals[0] = sig
                else:
                    minima = sig
            else:
                state = 'e3'
                rsi_vals[1] = sig

        elif state == 'e3':
            if sig >= rsi_vals[1]:
                prices[1] = position['Close'][i]
                rsi_vals[1] = sig
            else:
                if rsi_vals[1] >= ovb_th[i]:
                    if (prices[1] > prices[0]) and (rsi_vals[0] > rsi_vals[1]):
                        # Bearish divergence!
                        divs[i] = -1.0
                        rsi_data['bearish'].append([
                            date_extractor(position.index[i], _format='str'),
                            position['Close'][i],
                            i,
                            "divergence"
                        ])
                        state = 'n'
                    else:
                        state = 'n'
                else:
                    state = 'n'

    rsi_data['divergence'] = divs

    if plot_output:
        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **dict(
                y_list_2=divs, y1_label='Price', y2_label='relative_strength_indicator_rsi',
                title='Divs'
            )
        )

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    return rsi_data


def rsi_metrics(rsi: dict, **kwargs) -> dict:
    """relative_strength_indicator_rsi Metrics

    Arguments:
        rsi {dict} -- rsi data object

    Optional Args:
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- rsi data object
    """
    # pylint: disable=too-many-branches
    p_bar = kwargs.get('p_bar')
    swings = rsi['indicator']
    divs = rsi['divergence']

    # Take indicator sets: weight, combine, filter, normalize
    weights = [1.0, 0.85, 0.55, 0.1]
    state2 = [0.0] * len(divs)

    for ind, s_val in enumerate(divs):
        if s_val != 0.0:
            state2[ind] += s_val

            # Smooth the curves
            if ind - 1 >= 0:
                state2[ind-1] += s_val * weights[1]
            if ind + 1 < len(divs):
                state2[ind+1] += s_val * weights[1]
            if ind - 2 >= 0:
                state2[ind-2] += s_val * weights[2]
            if ind + 2 < len(divs):
                state2[ind+2] += s_val * weights[2]
            if ind - 3 >= 0:
                state2[ind-3] += s_val * weights[3]
            if ind + 3 < len(divs):
                state2[ind+3] += s_val * weights[3]

    if p_bar is not None:
        p_bar.uptick(increment=0.05)

    for ind, s_val in enumerate(swings):
        if s_val != 0.0:
            state2[ind] += s_val

            # Smooth the curves
            if ind - 1 >= 0:
                state2[ind-1] += s_val * weights[1]
            if ind + 1 < len(swings):
                state2[ind+1] += s_val * weights[1]
            if ind - 2 >= 0:
                state2[ind-2] += s_val * weights[2]
            if ind + 2 < len(swings):
                state2[ind+2] += s_val * weights[2]
            if ind - 3 >= 0:
                state2[ind-3] += s_val * weights[3]
            if ind + 3 < len(swings):
                state2[ind+3] += s_val * weights[3]

    if p_bar is not None:
        p_bar.uptick(increment=0.05)

    metrics = exponential_moving_avg(state2, 7, data_type='list')
    norm = normalize_signals([metrics])
    metrics = norm[0]

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    rsi['metrics'] = metrics
    return rsi


def rsi_signals(bull_list: list, bear_list: list) -> list:
    """relative_strength_indicator_rsi Signals

    Format all rsi signals into a single list

    Arguments:
        bull_list {list} -- list of bullish signals
        bear_list {list} -- list of bearish signals

    Returns:
        list -- list of rsi signals
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
