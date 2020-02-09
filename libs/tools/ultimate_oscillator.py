import pandas as pd
import numpy as np

from libs.utils import dual_plotting, date_extractor
from libs.utils import ProgressBar, SP500
from libs.features import normalize_signals
from .math_functions import lower_low, higher_high, bull_bear_th
from .moving_average import windowed_moving_avg


def generate_ultimate_osc_signal(position: pd.DataFrame, config: list = [7, 14, 28], **kwargs) -> list:
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
    p_bar = kwargs.get('p_bar')

    tot_len = len(position['Close'])
    SHORT = config[0]
    MED = config[1]
    LONG = config[2]

    bp = [0.0] * tot_len
    tr = [0.0] * tot_len
    ushort = [0.0] * tot_len
    umed = [0.0] * tot_len
    ulong = [0.0] * tot_len

    ult_osc = [50.0] * tot_len

    # Generate the ultimate oscillator values
    for i in range(1, tot_len):

        low = np.min([position['Low'][i], position['Close'][i-1]])
        high = np.max([position['High'][i], position['Close'][i-1]])
        bp[i] = np.round(position['Close'][i] - low, 6)
        tr[i] = np.round(high - low, 6)

        if i >= SHORT-1:
            shbp = sum(bp[i-SHORT: i+1])
            shtr = sum(tr[i-SHORT: i+1])
            if shtr != 0.0:
                ushort[i] = np.round(shbp / shtr, 6)

        if i >= MED-1:
            shbp = sum(bp[i-MED: i+1])
            shtr = sum(tr[i-MED: i+1])
            if shtr != 0.0:
                umed[i] = np.round(shbp / shtr, 6)

        if i >= LONG-1:
            shbp = sum(bp[i-LONG: i+1])
            shtr = sum(tr[i-LONG: i+1])
            if shtr != 0.0:
                ulong[i] = np.round(shbp / shtr, 6)
            ult_osc[i] = \
                np.round(
                    100.0 * ((4.0 * ushort[i]) + (2.0 * umed[i]) + ulong[i]) / 7.0, 6)

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    return ult_osc


def find_ult_osc_features(position: pd.DataFrame, ultimate: dict, **kwargs) -> list:
    """Find Ultimate Oscilator Features 

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
    p_bar = kwargs.get('p_bar')
    LOW_TH = kwargs.get('thresh_low', 30)
    HIGH_TH = kwargs.get('thresh_high', 70)

    ult_osc = ultimate['tabular']

    trigger = []
    marker_val = 0.0
    marker_ind = 0

    for i, close in enumerate(position['Close']):

        # Find bullish signal
        if ult_osc[i] < LOW_TH:
            ult1 = ult_osc[i]
            marker_val = close
            marker_ind = i
            lows = lower_low(position['Close'], marker_val, marker_ind)
            if len(lows) != 0:
                ult2 = ult_osc[lows[len(lows)-1][1]]

                if ult2 > ult1:
                    start_ind = lows[len(lows)-1][1]
                    interval = np.max(ult_osc[i:start_ind+1])
                    start_ind = bull_bear_th(
                        ult_osc, start_ind, interval, bull_bear='bull')
                    if start_ind is not None:
                        trigger.append(["BULLISH", date_extractor(
                            position.index[start_ind], _format='str'), position['Close'][start_ind], start_ind])

        # Find bearish signal
        if ult_osc[i] > HIGH_TH:
            ult1 = ult_osc[i]
            marker_val = position['Close'][i]
            marker_ind = i
            highs = higher_high(position['Close'], marker_val, marker_ind)
            if len(highs) != 0:
                ult2 = ult_osc[highs[len(highs)-1][1]]

                if ult2 < ult1:
                    start_ind = highs[len(highs)-1][1]
                    interval = np.min(ult_osc[i:start_ind+1])
                    start_ind = bull_bear_th(
                        ult_osc, start_ind, interval, bull_bear='bear')
                    if start_ind is not None:
                        trigger.append(["BEARISH", date_extractor(
                            position.index[start_ind], _format='str'), position['Close'][start_ind], start_ind])

    if p_bar is not None:
        p_bar.uptick(increment=0.3)

    state = 'n'
    prices = [0.0, 0.0]
    ults = [0.0, 0.0, 0.0]

    for i, ult in enumerate(ult_osc):

        # Find bullish divergence and breakout
        if (state == 'n') and (ult <= LOW_TH):
            state = 'u1'
            ults[0] = ult

        elif state == 'u1':
            if ult < ults[0]:
                ults[0] = ult
            else:
                prices[0] = position['Close'][i-1]
                state = 'u2'

        elif (state == 'u2') and (ult > LOW_TH):
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
                state == 'u5'

        elif state == 'u5':
            if ult > ults[1]:
                if prices[0] > prices[1]:
                    # Bullish breakout!
                    trigger.append(["BULLISH", date_extractor(
                        position.index[start_ind], _format='str'), position['Close'][start_ind], start_ind])
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
        if (state == 'n') and (ult >= HIGH_TH):
            state = 'e1'
            ults[0] = ult

        elif state == 'e1':
            if ult > ults[0]:
                ults[0] = ult
            else:
                prices[0] = position['Close'][i-1]
                state = 'e2'

        elif (state == 'e2') and (ult < HIGH_TH):
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
                state == 'e5'

        elif state == 'e5':
            if ult < ults[1]:
                if prices[0] < prices[1]:
                    # Bullish breakout!
                    trigger.append(["BEARISH", date_extractor(
                        position.index[start_ind], _format='str'), position['Close'][start_ind], start_ind])
                    state = 'n'
                else:
                    # False breakout, see if this is the new max:
                    state = 'e3'
                    ults[1] = ult
            elif ult > ults[2]:
                # There may have been a false signal
                ults[2] = ult
                state = 'e4'

        elif ult >= HIGH_TH:
            state = 'e1'
            ults[0] = ult

        elif ult <= LOW_TH:
            state = 'u1'
            ults[0] = ult

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    ultimate['indicator'] = trigger

    return ultimate


def ult_osc_output(ultimate: dict, len_of_position: int, **kwargs) -> list:
    """ Simplifies signals to easy to view plot and dictionary
    Returns:
        list:
            plot (list): easy signal to plot on top of a position's price plot
            ultimate (dict): dictionary of specific information represented by 'plot' signal

    """
    p_bar = kwargs.get('p_bar')

    ultimate['bullish'] = []
    ultimate['bearish'] = []

    trigger = ultimate['indicator']

    simplified = []
    plots = []
    for i in range(len_of_position):
        plots.append(0.0)
    present = False
    for i in range(len(trigger)):
        for j in range(len(simplified)):
            if simplified[j][3] == trigger[i][3]:
                present = True
        if not present:
            simplified.append(trigger[i])
            if trigger[i][0] == "BEARISH":
                plots[trigger[i][3]] = -1.0
                ultimate['bearish'].append(
                    [trigger[i][1], trigger[i][2], trigger[i][3]])
            else:
                plots[trigger[i][3]] = 1.0
                ultimate['bullish'].append(
                    [trigger[i][1], trigger[i][2], trigger[i][3]])
        present = False

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    ultimate['plots'] = plots

    return ultimate


def ultimate_osc_metrics(position: pd.DataFrame, ultimate: dict, **kwargs) -> dict:
    """Ultimate Oscillator Metrics

    Arguments:
        position {pd.DataFrame} -- dataset
        ultimate {dict} -- ultimate osc data object

    Optional Args:
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- ultimate osc data object
    """
    p_bar = kwargs.get('p_bar')
    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', True)
    name = kwargs.get('name', '')

    ults = ultimate['plots']

    # Take indicator set: weight, filter, normalize
    weights = [1.0, 0.9, 0.75, 0.45]
    state2 = [0.0] * len(ults)

    for ind, s in enumerate(ults):
        if s != 0.0:
            state2[ind] += s

            # Smooth the curves
            if ind - 1 >= 0:
                state2[ind-1] += s * weights[1]
            if ind + 1 < len(ults):
                state2[ind+1] += s * weights[1]
            if ind - 2 >= 0:
                state2[ind-2] += s * weights[2]
            if ind + 2 < len(ults):
                state2[ind+2] += s * weights[2]
            if ind - 3 >= 0:
                state2[ind-3] += s * weights[3]
            if ind + 3 < len(ults):
                state2[ind+3] += s * weights[3]

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    metrics = windowed_moving_avg(state2, 7, data_type='list')
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    norm = normalize_signals([metrics])
    metrics = norm[0]

    if not out_suppress:
        name3 = SP500.get(name, name)
        name2 = name3 + ' - Ultimate Oscillator Metrics'
        if plot_output:
            dual_plotting(position['Close'], metrics, 'Price',
                          'Metrics', title='Ultimate Oscillator Metrics')
        else:
            filename = name + f"/ultimate_osc_metrics_{name}.png"
            dual_plotting(position['Close'], metrics, 'Price',
                          'Metrics', title=name2, filename=filename, saveFig=True)

    ultimate['metrics'] = metrics
    return ultimate


def ultimate_oscillator(position: pd.DataFrame, config: list = [7, 14, 28], **kwargs) -> dict:
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
    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')

    ultimate = dict()

    ult_osc = generate_ultimate_osc_signal(
        position, config=config, p_bar=p_bar)
    ultimate['tabular'] = ult_osc

    ultimate = find_ult_osc_features(position, ultimate, p_bar=p_bar)

    ultimate = ult_osc_output(
        ultimate, len(position['Close']), p_bar=p_bar)

    ultimate = ultimate_osc_metrics(
        position, ultimate, plot_output=plot_output, out_suppress=out_suppress,
        name=name, p_bar=p_bar)

    if not out_suppress:
        name3 = SP500.get(name, name)
        name2 = name3 + ' - Ultimate Oscillator'
        if plot_output:
            dual_plotting(position['Close'], ult_osc, 'Position Price',
                          'Ultimate Oscillator', title=name2)
            dual_plotting(position['Close'], ultimate['plots'],
                          'Position Price', 'Buy-Sell Signal', title=name2)
        else:
            filename = name + '/ultimate_osc_{}.png'.format(name)
            dual_plotting(position['Close'], ult_osc, 'Position Price',
                          'Ultimate Oscillator', title=name2, saveFig=True, filename=filename)
            dual_plotting(position['Close'], ultimate['plots'], 'Position Price',
                          'Buy-Sell Signal', title=name2, saveFig=True, filename=filename)

    return ultimate
