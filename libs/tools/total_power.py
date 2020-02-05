import pandas as pd
import numpy as np

from libs.tools import exponential_moving_avg, windowed_moving_avg
from libs.utils import dual_plotting, generic_plotting
from libs.utils import SP500
from libs.features import normalize_signals


def total_power(position: pd.DataFrame, **kwargs) -> dict:
    """Total Power

    Calculation of Bull Power / Bear Power with additional wrinkles

    Arguments:
        position {pd.DataFrame} -- dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- total power data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')

    tp = dict()

    tp['tabular'] = generate_total_power_signal(
        position, plot_output=plot_output, p_bar=p_bar, name=name)

    tp = total_power_feature_detection(
        tp, position, plot_output=plot_output, name=name, p_bar=p_bar)

    return tp


def generate_total_power_signal(position: pd.DataFrame, **kwargs) -> dict:
    """Generate Total Power Signal

    Arguments:
        position {pd.DataFrame} -- dataset

    Optional Args:
        lookback {int} -- period for total power signal (default: {45})
        powerback {int} -- period for ema (default: {10})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- cumulative signals bear, bull, total
    """
    lookback = kwargs.get('lookback', 45)
    powerback = kwargs.get('powerback', 10)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('p_bar')

    signals = {"bears_raw": [], "bulls_raw": [],
               "total": [], "bears": [], "bulls": []}

    ema = exponential_moving_avg(position, powerback)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    for i, high in enumerate(position['High']):
        if high - ema[i] > 0.0:
            signals['bulls_raw'].append(1.0)
        else:
            signals['bulls_raw'].append(0.0)
    for i, low in enumerate(position['Low']):
        if low - ema[i] < 0.0:
            signals['bears_raw'].append(1.0)
        else:
            signals['bears_raw'].append(0.0)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    # Create look back period signals
    for i in range(lookback-1):
        signals['bulls'].append(sum(signals['bulls_raw'][0:i+1]))
        signals['bears'].append(sum(signals['bears_raw'][0:i+1]))

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    for i in range(lookback-1, len(ema)):
        summer = sum(signals['bulls_raw'][i-(lookback-1): i])
        signals['bulls'].append(summer)
        summer = sum(signals['bears_raw'][i-(lookback-1): i])
        signals['bears'].append(summer)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    # Compute the total power signal
    for i, bull in enumerate(signals['bulls']):
        total = np.abs(bull - signals['bears'][i])
        signals['total'].append(total)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    # Adjust the signals, pop the 'raw' lists
    signals.pop('bulls_raw')
    signals.pop('bears_raw')

    for i, tot in enumerate(signals['total']):
        signals['total'][i] = 100.0 * tot / float(lookback)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    for i, bull in enumerate(signals['bulls']):
        signals['bulls'][i] = 100.0 * bull / float(lookback)
    for i, bear in enumerate(signals['bears']):
        signals['bears'][i] = 100.0 * bear / float(lookback)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    name2 = SP500.get(name, name)
    title = name2 + ' - Total Power'
    if plot_output:
        dual_plotting(position['Close'], [
                      signals['bears'], signals['bulls'], signals['total']], 'Price', ['Bear', 'Bull', 'Total'],
                      title=title)
    else:
        filename = name + f'/total_power_{name}'
        dual_plotting(position['Close'], [signals['bears'], signals['bulls'], signals['total']], 'Price', ['Bear', 'Bull', 'Total'],
                      title=title, saveFig=True, filename=filename)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    return signals


def total_power_feature_detection(tp: dict, position: pd.DataFrame, **kwargs) -> dict:
    """Total Power Feature Detection / Metrics

    Arguments:
        tp {dict} -- total power data object
        position {pd.DataFrame} -- dataset

    Optional Args:
        adj_level {float} -- threshold level of indicators (default: {72.0})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- tp
    """
    adj_level = kwargs.get('adj_level', 72.0)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('p_bar')

    tab = tp['tabular']
    metrics = [0.0] * len(tab['total'])

    if tab['bulls'][0] > tab['bears'][0]:
        on_top = 'bull'
    else:
        on_top = 'bear'

    tot_above = ''
    for i, tot in enumerate(tab['total']):
        if (tot >= 99.0) and (tab['bulls'][i] >= 99.0):
            metrics[i] += 3.0

        if (tot >= 99.0) and (tab['bears'][i] >= 99.0):
            metrics[i] += -3.0

        if (on_top == 'bull') and (tab['bears'][i] > tab['bulls'][i]):
            metrics[i] += -1.0
            on_top = 'bear'

        if (on_top == 'bear') and (tab['bulls'][i] > tab['bears'][i]):
            metrics[i] += -1.0
            on_top = 'bull'

        if tot > tab['bulls'][i]:
            tot_above = 'bull'

        if tot > tab['bears'][i]:
            tot_above = 'bear'

        if (tot_above == 'bull') and (tab['bulls'][i] > tot):
            tot_above = ''
            metrics[i] += 1.0

        if (tot_above == 'bear') and (tab['bears'][i] > tot):
            tot_above = ''
            metrics[i] += -1.0

        if i > 0:
            if (tab['bulls'][i-1] < adj_level) and (tab['bulls'][i] > adj_level):
                metrics[i] += 1.0

            if (tab['bears'][i-1] < adj_level) and (tab['bears'][i] > adj_level):
                metrics[i] += -1.0

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    weights = [1.0, 0.85, 0.6, 0.25]

    state2 = [0.0] * len(metrics)
    for ind, s in enumerate(metrics):
        if s != 0.0:
            state2[ind] += s

            # Smooth the curves
            if ind - 1 >= 0:
                state2[ind-1] += s * weights[1]
            if ind + 1 < len(metrics):
                state2[ind+1] += s * weights[1]
            if ind - 2 >= 0:
                state2[ind-2] += s * weights[2]
            if ind + 2 < len(metrics):
                state2[ind+2] += s * weights[2]
            if ind - 3 >= 0:
                state2[ind-3] += s * weights[3]
            if ind + 3 < len(metrics):
                state2[ind+3] += s * weights[3]

    metrics = windowed_moving_avg(state2, 7, data_type='list')
    norm = normalize_signals([metrics])
    metrics = norm[0]

    name2 = SP500.get(name, name)
    title = name2 + ' - Total Power Metrics'
    if plot_output:
        dual_plotting(position['Close'], metrics, 'Price', 'Metrics')
    else:
        filename = name + f'/total_power_metrics_{name}'
        dual_plotting(position['Close'], metrics, 'Price',
                      'Metrics', title=title, saveFig=True, filename=filename)

    tp['metrics'] = metrics

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    return tp
