import os
import pandas as pd
import numpy as np

from libs.utils import date_extractor, INDEXES, PlotType, generate_plot
from libs.features import normalize_signals

from .moving_average import exponential_moving_avg


def full_stochastic(position: pd.DataFrame, config: list = [14, 3, 3], **kwargs) -> dict:
    """Full Stochastic

    Typical periods are [14, 3, 3], [10, 3, 3], [20, 5, 5]

    Arguments:
        position {pd.DataFrame} -- dataset

    Keyword Arguments:
        config {list} -- look back periods: fast %k, slow %k, slow %d (default: {[14, 3, 3]})

    Optional Args:
        name {str} -- (default: {''})
        plot_output {bool} -- (default: {True})
        out_suppress {bool} -- suppresses plotting for clusters (default: {True})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- [description]
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    out_suppress = kwargs.get('out_suppress', True)
    progress_bar = kwargs.get('progress_bar')
    view = kwargs.get('view', '')

    full_stoch = dict()

    signals = generate_full_stoch_signal(
        position, periods=config, plot_output=plot_output,
        out_suppress=out_suppress, p_bar=progress_bar, view=view)
    full_stoch['tabular'] = signals

    full_stoch = get_crossover_features(
        position, full_stoch, p_bar=progress_bar)

    full_stoch = get_stoch_divergences(
        position, full_stoch, plot_output=plot_output,
        out_suppress=out_suppress, name=name, p_bar=progress_bar, view=view)

    full_stoch = get_stoch_metrics(
        position, full_stoch, plot_output=plot_output, name=name, p_bar=progress_bar)

    full_stoch['signals'] = get_stoch_signals(
        full_stoch['bullish'], full_stoch['bearish'])

    full_stoch['type'] = 'oscillator'
    full_stoch['length_of_data'] = len(full_stoch['tabular']['fast_k'])

    return full_stoch


def generate_full_stoch_signal(position: pd.DataFrame, periods=[14, 3, 3], **kwargs) -> dict:
    """Generate Full Stochastic Signal

    For fast/normal stochastic signals: %k, slow %k (which is %d for fast stochastics)
    For slow stochastic signals: slow %k, %d

    Arguments:
        position {pd.DataFrame} -- dataset

    Keyword Arguments:
        periods {list} -- %k, slow %k, slow %d (default: {[14, 3, 3]})

    Optional Args:
        plot_output {bool} -- (default: {True})
        out_suppress {bool} -- (default: {True})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- tabular object of signals {"fast_k", "smooth_k", "slow_d"}
    """
    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', True)
    p_bar = kwargs.get('p_bar')

    FAST_K = periods[0]
    SLOW_K = periods[1]
    SLOW_D = periods[2]

    k_instant = []
    k_smooth = []
    d_sma = []

    for i in range(FAST_K-1):
        k_instant.append(50.0)
        k_smooth.append(50.0)
        d_sma.append(50.0)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    for i in range(FAST_K-1, len(position['Close'])):

        # Find first lookback of oscillator
        lows = position['Low'][i-(FAST_K-1):i+1]
        highs = position['High'][i-(FAST_K-1):i+1]
        low = np.min(lows)
        high = np.max(highs)

        # For very low cost funds with no movement over range, will be NaN
        if low != high:
            K = (position['Close'][i] - low) / (high - low) * 100.0
        else:
            K = 50.0

        k_instant.append(K)

        # Smooth oscillator with config[1]
        k_smooth.append(np.average(k_instant[i-(SLOW_K-1):i+1]))

        # Find 'Simple Moving Average' (SMA) of k2
        d_sma.append(np.average(k_smooth[i-(SLOW_D-1):i+1]))

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    if not out_suppress and plot_output:
        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **dict(
                y_list_2=[k_instant, k_smooth, d_sma], y1_label='Price',
                y2_label=['Fast %K, Slow %K, Slow %D']
            )
        )

    signals = {"fast_k": k_instant, "smooth_k": k_smooth, "slow_d": d_sma}

    return signals


def get_crossover_features(position: pd.DataFrame, full_stoch: dict, **kwargs) -> dict:
    """Get Crossover Features

    Look for a %K cross over %d (fast) then cross inside the 80/20 bars.
    Look for a slow %K cross over slow %d then cross inside the 80/20 bars.

    Arguments:
        position {pd.DataFrame} -- dataset
        full_stoch {dict} -- full stochastic object

    Optional Args:
        p_bar {ProgressBar} -- (default: {None}) 

    Returns:
        dict -- full stochastic object
    """
    p_bar = kwargs.get('p_bar')

    OVER_BOUGHT = 80.0
    OVER_SOLD = 20.0

    fast_k = full_stoch['tabular']['fast_k']
    smooth_k = full_stoch['tabular']['smooth_k']
    d_sma = full_stoch['tabular']['slow_d']

    bearish = []
    bullish = []
    stochastic = [0.0] * (len(fast_k))
    state = 'n'

    # Look at crossovers and over-X positions of fast_k & smooth_k
    for i, fast in enumerate(fast_k):

        # Bearish / overbought signaling
        if (state == 'n') and (fast >= OVER_BOUGHT):
            state = 'b1'

        elif (state == 'b1'):
            if (fast >= OVER_BOUGHT):
                if (smooth_k[i] >= OVER_BOUGHT):
                    state = 'b2'
            else:
                state = 'n'

        elif (state == 'b2') and (fast < smooth_k[i]):
            state = 'b3'

        elif (state == 'b3'):
            if (fast < OVER_BOUGHT):
                bearish.append([
                    date_extractor(position.index[i], _format='str'),
                    position['Close'][i],
                    i,
                    "crossover: fast-k/smooth-k"
                ])
                stochastic[i] += -1.0
                state = 'n'

        # Bullish / oversold signaling
        elif (state == 'n') and (fast <= OVER_SOLD):
            state = 's1'

        elif (state == 's1'):
            if (fast <= OVER_SOLD):
                if (smooth_k[i] <= OVER_SOLD):
                    state = 's2'
            else:
                state = 'n'

        elif (state == 's2') and (fast > smooth_k[i]):
            state = 's3'

        elif (state == 's3'):
            if (fast > OVER_SOLD):
                bullish.append([
                    date_extractor(position.index[i], _format='str'),
                    position['Close'][i],
                    i,
                    "crossover: fast-k/smooth-k"
                ])
                stochastic[i] += 1.0
                state = 'n'

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    # Look at crossovers and over-X positions of smooth_k & slow_d
    state = 'n'
    for i, slow in enumerate(smooth_k):

        # Bearish / overbought signaling
        if (state == 'n') and (slow >= OVER_BOUGHT):
            state = 'b1'

        elif (state == 'b1'):
            if (slow >= OVER_BOUGHT):
                if (d_sma[i] >= OVER_BOUGHT):
                    state = 'b2'
            else:
                state = 'n'

        elif (state == 'b2') and (slow < d_sma[i]):
            state = 'b3'

        elif (state == 'b3'):
            if (slow < OVER_BOUGHT):
                bearish.append([
                    date_extractor(position.index[i], _format='str'),
                    position['Close'][i],
                    i,
                    "crossover: smooth-k/slow-d"
                ])
                stochastic[i] += -1.0
                state = 'n'

        # Bullish / oversold signaling
        elif (state == 'n') and (slow <= OVER_SOLD):
            state = 's1'

        elif (state == 's1'):
            if (slow <= OVER_SOLD):
                if (d_sma[i] <= OVER_SOLD):
                    state = 's2'
            else:
                state = 'n'

        elif (state == 's2') and (slow > d_sma[i]):
            state = 's3'

        elif (state == 's3'):
            if (slow > OVER_SOLD):
                bullish.append([
                    date_extractor(position.index[i], _format='str'),
                    position['Close'][i],
                    i,
                    "crossover: smooth-k/slow-d"
                ])
                stochastic[i] += 1.0
                state = 'n'

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    full_stoch['indicator'] = stochastic
    full_stoch['bullish'] = bullish
    full_stoch['bearish'] = bearish

    return full_stoch


def get_stoch_divergences(position: pd.DataFrame, full_stoch: dict, **kwargs) -> dict:
    """Get Stoch Divergences

    Arguments:
        position {pd.DataFrame} -- dataset
        full_stoch {dict} -- stoch data object

    Optional Args:
        name {str} -- (default: {''})
        plot_output {bool} -- (default: {True})
        out_suppress {bool} -- (default: {True})
        p_bar {ProgressBar} -- (default: {None}) 

    Returns:
        dict -- stoch data object
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', True)
    p_bar = kwargs.get('p_bar')
    view = kwargs.get('view')

    OVER_BOUGHT = 80.0
    OVER_SOLD = 20.0

    fast_k = full_stoch['tabular']['fast_k']
    state = 'n'

    # Look for divergences + fast_k at 50
    prices = [0.0, 0.0]
    s_vals = [0.0, 0.0]
    for i, fast in enumerate(fast_k):

        # Bearish divergences
        if (state == 'n') and fast >= OVER_BOUGHT:
            state = 'b1'
            s_vals[0] = fast

        elif state == 'b1':
            if fast < s_vals[0]:
                prices[0] = position['Close'][i]
                state = 'b2'
            else:
                s_vals[0] = fast

        elif state == 'b2':
            if fast < OVER_BOUGHT:
                state = 'b3'
                s_vals[1] = fast
            elif fast > s_vals[0]:
                s_vals[0] = fast
                state = 'b1'

        elif state == 'b3':
            if fast > s_vals[1]:
                state = 'b4'
                s_vals[1] = fast
            else:
                s_vals[1] = fast

        elif state == 'b4':
            if fast < s_vals[1]:
                prices[1] = position['Close'][i-1]
                if (prices[0] < prices[1]) and (s_vals[0] > s_vals[1]):
                    full_stoch['bearish'].append([
                        date_extractor(position.index[i], _format='str'),
                        position['Close'][i-1],
                        i,
                        "divergence"
                    ])
                    full_stoch['indicator'][i] += -1.5
                    state = 'n'
                else:
                    state = 'n'
            else:
                s_vals[1] = fast
                if s_vals[1] > s_vals[0]:
                    s_vals[0] = fast
                    state = 'b1'

        # Bullish divergences
        elif (state == 'n') and fast <= OVER_SOLD:
            state = 's1'
            s_vals[0] = fast

        elif state == 's1':
            if fast > s_vals[0]:
                prices[0] = position['Close'][i]
                state = 's2'
            else:
                s_vals[0] = fast

        elif state == 's2':
            if fast > OVER_SOLD:
                state = 's3'
                s_vals[1] = fast
            elif fast < s_vals[0]:
                s_vals[0] = fast
                state = 's1'

        elif state == 's3':
            if fast < s_vals[1]:
                state = 's4'
                s_vals[1] = fast
            else:
                s_vals[1] = fast

        elif state == 's4':
            if fast > s_vals[1]:
                prices[1] = position['Close'][i-1]
                if (prices[0] > prices[1]) and (s_vals[0] < s_vals[1]):
                    full_stoch['bullish'].append([
                        date_extractor(position.index[i], _format='str'),
                        position['Close'][i-1],
                        i,
                        "divergence"
                    ])
                    full_stoch['indicator'][i] += 1.5
                    state = 'n'
                else:
                    state = 'n'
            else:
                s_vals[1] = fast
                if s_vals[1] < s_vals[0]:
                    s_vals[0] = fast
                    state = 's1'

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    if not out_suppress:
        name3 = INDEXES.get(name, name)
        name2 = name3 + ' - Stochastic'

        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **dict(
                y_list_2=full_stoch['indicator'], y1_label='Position Price',
                y2_label='Oscillator Signal', title=name2, plot_output=plot_output,
                filename=os.path.join(name, view, f"stochastic_{name}.png")
            )
        )

    return full_stoch


def get_stoch_metrics(position: pd.DataFrame, full_stoch: dict, **kwargs) -> dict:
    """Get Stochastic Metrics

    Arguments:
        position {pd.DataFrame} -- dataset
        full_stoch {dict} -- stochastic data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        p_bar {ProgressBar} -- {default: {None}}

    Returns:
        dict -- stochastic data object
    """
    plot_output = kwargs.get('plot_output', True)
    p_bar = kwargs.get('p_bar')

    stochs = full_stoch['indicator']

    # Take indicator set: weight, filter, normalize
    weights = [1.0, 0.85, 0.55, 0.1]
    state2 = [0.0] * len(stochs)

    for ind, s in enumerate(stochs):
        if s != 0.0:
            state2[ind] += s

            # Smooth the curves
            if ind - 1 >= 0:
                state2[ind-1] += s * weights[1]
            if ind + 1 < len(stochs):
                state2[ind+1] += s * weights[1]
            if ind - 2 >= 0:
                state2[ind-2] += s * weights[2]
            if ind + 2 < len(stochs):
                state2[ind+2] += s * weights[2]
            if ind - 3 >= 0:
                state2[ind-3] += s * weights[3]
            if ind + 3 < len(stochs):
                state2[ind+3] += s * weights[3]

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    metrics = exponential_moving_avg(state2, 7, data_type='list')
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    norm = normalize_signals([metrics])
    metrics = norm[0]

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    full_stoch['metrics'] = metrics

    if plot_output:
        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **dict(
                y_list_2=metrics, y1_label='Price', y2_label='Metrics', title='Stochastic Metrics',
            )
        )

    return full_stoch


def get_stoch_signals(bull_list: list, bear_list: list) -> list:
    """get_stoch_signals

    Format all stochastic signals into a single list

    Arguments:
        bull_list {list} -- list of bullish signals
        bear_list {list} -- list of bearish signals

    Returns:
        list -- list of stochastic signals
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
