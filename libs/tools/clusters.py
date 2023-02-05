import os
import pandas as pd
import numpy as np

from libs.utils import date_extractor, INDEXES, STANDARD_COLORS, PlotType, generate_plot
from libs.features import normalize_signals

from .ultimate_oscillator import ultimate_oscillator
from .rsi import relative_strength_indicator_rsi
from .full_stochastic import full_stochastic

from .moving_average import exponential_moving_avg
from .trends import auto_trend

WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]

BASE_WEIGHTS = {
    'stoch': 2,
    'rsi': 3,
    'ultimate': 7
}


def cluster_oscillators(position: pd.DataFrame, **kwargs):
    """
    2-3-5-8 multiplier comparing several different osc lengths

    Arguments:
        position {pd.DataFrame} -- list of y-value datasets to be plotted (multiple)

    Optional Args:
        name {str} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        function {str} -- type of oscillator (default: {'full_stochastic'}) 
                                (others: ultimate, rsi, all, market)
        wma {bool} -- output signal is filtered by windowed moving average (default: {True})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- file directory of plots (default: {''})

    Returns:
        list -- dict of all clustered oscillator info, list of clustered osc signal
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    function = kwargs.get('function', 'full_stochastic')
    wma = kwargs.get('wma', True)
    prog_bar = kwargs.get('progress_bar', None)
    view = kwargs.get('view', '')

    cluster_oscillators = {}

    clusters = generate_cluster(position, function, p_bar=prog_bar)
    cluster_oscillators['tabular'] = clusters
    cluster_oscillators['length_of_data'] = len(clusters)

    #clusters_filtered = cluster_filtering(clusters, filter_thresh)
    clusters_wma = exponential_moving_avg(
        clusters, interval=3, data_type='list')
    if prog_bar is not None:
        prog_bar.uptick(increment=0.1)

    dates = cluster_dates(clusters_wma, position)
    if prog_bar is not None:
        prog_bar.uptick(increment=0.1)

    signals = clustered_signals(dates)
    if prog_bar is not None:
        prog_bar.uptick(increment=0.1)

    cluster_oscillators['clustered type'] = function
    cluster_oscillators[function] = dates
    cluster_oscillators['signals'] = signals

    cluster_oscillators = clustered_metrics(
        position, cluster_oscillators, plot_output=plot_output, name=name, view=view)

    name3 = INDEXES.get(name, name)
    name2 = name3 + ' - Clustering: ' + function
    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **dict(
            y_list_2=clusters, y1_label='Position Price', y2_label='Clustered Oscillator',
            x_label='Trading Days', title=name2, plot_output=plot_output,
            filename=os.path.join(name, view, f"clustering_{name}_{function}")
        )
    )

    if prog_bar is not None:
        prog_bar.uptick(increment=0.2)

    if wma:
        cluster_oscillators['tabular'] = clusters_wma

    cluster_oscillators['type'] = 'oscillator'

    return cluster_oscillators


def clustering(updatable: list, evaluator: dict, **kwargs) -> list:
    """Clustering

    Arguments:
        updatable {list} -- cluster at each index
        evaluator {dict} -- either bullish or bearish

    Keyword Arguments:
        weight {list} -- (default: {[]})

    Returns:
        list -- updateable returned
    """
    weight = kwargs.get('weight', [])
    if len(weight) == 0:
        for _ in range(len(updatable)):
            weight.append(1)
    for bull in evaluator['bullish']:
        index = bull[2]
        updatable[index] += (8*weight[index]) if updatable[index] != 0 else 1
        if index < len(updatable)-1:
            updatable[index-1] += (5*weight[index]
                                   ) if updatable[index-1] != 0 else 0
            updatable[index+1] += (5*weight[index]
                                   ) if updatable[index+1] != 0 else 0
        if index < len(updatable)-2:
            updatable[index-2] += (3*weight[index]
                                   ) if updatable[index-2] != 0 else 0
            updatable[index+2] += (3*weight[index]
                                   ) if updatable[index+2] != 0 else 0
        if index < len(updatable)-3:
            updatable[index-3] += (2*weight[index]
                                   ) if updatable[index-3] != 0 else 0
            updatable[index+3] += (2*weight[index]
                                   ) if updatable[index+3] != 0 else 0

    for bear in evaluator['bearish']:
        index = bear[2]
        updatable[index] += (-8*weight[index]) if updatable[index] != 0 else -1
        if index < len(updatable)-1:
            updatable[index-1] += (-5*weight[index]
                                   ) if updatable[index-1] != 0 else 0
            updatable[index+1] += (-5*weight[index]
                                   ) if updatable[index+1] != 0 else 0
        if index < len(updatable)-2:
            updatable[index-2] += (-3*weight[index]
                                   ) if updatable[index-2] != 0 else 0
            updatable[index+2] += (-3*weight[index]
                                   ) if updatable[index+2] != 0 else 0
        if index < len(updatable)-3:
            updatable[index-3] += (-2*weight[index]
                                   ) if updatable[index-3] != 0 else 0
            updatable[index+3] += (-2*weight[index]
                                   ) if updatable[index+3] != 0 else 0

    return updatable


def cluster_filtering(cluster_list: list, filter_thresh: int = 7) -> list:
    """ Filters a clustered projection such that any x for (-filter_thresh < f[x] < filter_thresh) = 0 """
    for i in range(len(cluster_list)):
        if (cluster_list[i] < filter_thresh) and (cluster_list[i] > -filter_thresh):
            cluster_list[i] = 0

    return cluster_list


def cluster_dates(cluster_list: list, fund: pd.DataFrame) -> list:
    """ Adds non-zero cluster values with date, price, and index """
    dates = []
    for i in range(len(cluster_list)):
        if cluster_list[i] != 0:
            dates.append([date_extractor(fund.index[i], _format='str'),
                          fund['Close'][i], cluster_list[i], i])
    return dates


def generate_cluster(position: pd.DataFrame, function: str, name='', p_bar=None) -> list:
    """Generate Cluster

    Subfunction to do clustering (removed from main for flexibility)

    Arguments:
        position {pd.DataFrame} -- fund dataset
        function {str} -- function to develop cluster signal 

    Keyword Arguments:
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- cluster signal
    """
    clusters = []

    for _ in range(len(position)):
        clusters.append(0)

    if function == 'full_stochastic':
        fast = full_stochastic(
            position, config=[10, 3, 3], plot_output=False, name=name)
        med = full_stochastic(
            position, config=[14, 3, 3], plot_output=False, name=name)
        slow = full_stochastic(
            position, config=[20, 5, 5], plot_output=False, name=name)

    elif function == 'ultimate':
        fast = ultimate_oscillator(
            position, config=[4, 8, 16], plot_output=False, name=name)
        med = ultimate_oscillator(
            position, config=[7, 14, 28], plot_output=False, name=name)
        slow = ultimate_oscillator(
            position, config=[10, 20, 40], plot_output=False, name=name)

    elif function == 'rsi':
        fast = relative_strength_indicator_rsi(position, plot_output=False, period=8, name=name)
        med = relative_strength_indicator_rsi(position, plot_output=False, period=14, name=name)
        slow = relative_strength_indicator_rsi(position, plot_output=False, period=20)

    elif function == 'all':
        fast_stoch = full_stochastic(
            position, config=[10, 3, 3], plot_output=False, name=name)
        med_stoch = full_stochastic(
            position, config=[14, 3, 3], plot_output=False, name=name)
        slow_stoch = full_stochastic(
            position, config=[20, 5, 5], plot_output=False, name=name)
        fast_ult = ultimate_oscillator(
            position, config=[5, 10, 20], plot_output=False, name=name)
        med_ult = ultimate_oscillator(
            position, config=[7, 14, 28], plot_output=False, name=name)
        slow_ult = ultimate_oscillator(
            position, config=[10, 20, 40], plot_output=False, name=name)
        fast_rsi = relative_strength_indicator_rsi(position, plot_output=False, period=8, name=name)
        med_rsi = relative_strength_indicator_rsi(position, plot_output=False, period=14, name=name)
        slow_rsi = relative_strength_indicator_rsi(position, plot_output=False, period=20, name=name)

    elif function == 'market':
        fast = full_stochastic(
            position, config=[14, 3, 3], plot_output=False, name=name)
        med = ultimate_oscillator(
            position, config=[7, 14, 28], plot_output=False, name=name)
        slow = relative_strength_indicator_rsi(position, plot_output=False, period=14, name=name)

    else:
        print(
            f'{WARNING}Warning: Unrecognized function input of {function} in cluster_oscillators.{NORMAL}')
        return None

    if p_bar is not None:
        p_bar.uptick(increment=0.25)

    if function == 'all':
        weights = generate_weights(position)

        clusters = clustering(clusters, fast_stoch,
                              weight=weights['stoch']['fast'])
        clusters = clustering(clusters, med_stoch,
                              weight=weights['stoch']['medium'])
        clusters = clustering(clusters, slow_stoch,
                              weight=weights['stoch']['slow'])
        clusters = clustering(clusters, fast_rsi,
                              weight=weights['rsi']['fast'])
        clusters = clustering(
            clusters, med_rsi, weight=weights['rsi']['medium'])
        clusters = clustering(clusters, slow_rsi,
                              weight=weights['rsi']['slow'])
        clusters = clustering(clusters, fast_ult,
                              weight=weights['ultimate']['fast'])
        clusters = clustering(
            clusters, med_ult, weight=weights['ultimate']['medium'])
        clusters = clustering(clusters, slow_ult,
                              weight=weights['ultimate']['slow'])
    else:
        clusters = clustering(clusters, fast)
        clusters = clustering(clusters, med)
        clusters = clustering(clusters, slow)

    if p_bar is not None:
        p_bar.uptick(increment=0.25)

    return clusters


def generate_weights(position, **kwargs) -> dict:
    """Generate Weights

    Using trend slopes, will assign slightly different weights to each oscillator

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        types {list} -- types of functions (default: {['stoch', 'rsi', 'ultimate']})
        speeds {list} -- types of speeds (default: {['fast', 'medium', 'slow']})

    Returns:
        dict -- cluster weights
    """
    types = kwargs.get('types', ['stoch', 'rsi', 'ultimate'])
    speeds = kwargs.get('speeds', ['fast', 'medium', 'slow'])

    trend = auto_trend(position['Close'], periods=[28, 56, 84], weights=[
                      0.3, 0.4, 0.3], normalize=True)

    weights = dict()
    for t in types:
        weights[t] = {}
        for s in speeds:
            if s == 'medium':
                wt = BASE_WEIGHTS[t]
            elif s == 'fast':
                wt = int(np.floor(float(BASE_WEIGHTS[t]) / 2.0))
            else:
                wt = int(np.ceil(float(BASE_WEIGHTS[t]) / 2.0))
            weights[t][s] = [wt for _ in range(len(position['Close']))]

    for i, t in enumerate(trend):
        if t >= -0.1 and t <= 0.1:
            for s in speeds:
                wt = weights['stoch'][s][i]
                weights['stoch'][s][i] = wt + 1
        else:
            for s in speeds:
                wt = weights['rsi'][s][i]
                weights['rsi'][s][i] = wt + 1

    return weights


def clustered_metrics(position: pd.DataFrame, cluster_oscillators: dict, **kwargs) -> dict:
    """Clustered Metrics

    Arguments:
        position {pd.DataFrame} -- dataset
        cluster_oscillators {dict} -- clustered osc data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- file directory of plots (default: {''})

    Returns:
        dict -- clustered osc data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view')

    ults = cluster_oscillators['tabular']

    # Take indicator set: weight, filter, normalize
    weights = [1.0, 0.85, 0.55, 0.1]
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

    metrics = exponential_moving_avg(state2, 7, data_type='list')
    norm = normalize_signals([metrics])
    metrics = norm[0]

    cluster_oscillators['metrics'] = metrics

    name3 = INDEXES.get(name, name)
    name2 = name3 + " - Clustered Oscillator Metrics"
    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **dict(
            y_list_2=metrics, y1_label='Price', y2_label='Metrics', title=name2,
            plot_output=plot_output,
            filename=os.path.join(name, view, f"clustered_osc_metrics_{name}.png")
        )
    )

    return cluster_oscillators


def clustered_signals(sig_list: list, **kwargs) -> list:
    """clustered_signals

    List a thresholded-set of clustered oscillator signals

    Arguments:
        sig_list {list} -- list of signals != 0

    Optional Args:
        upper_thresh {int} -- upper percentile (default: {90})
        lower_thresh {int} -- lower percentile (default: {10})

    Returns:
        list -- filtered clustered oscillator signals
    """
    upper_thresh = kwargs.get('upper_thresh', 90)
    lower_thresh = kwargs.get('lower_thresh', 10)

    quartiles = [x[2] for x in sig_list]
    upper = np.percentile(quartiles, upper_thresh)
    lower = np.percentile(quartiles, lower_thresh)

    signals_of_note = []
    for sig in sig_list:
        if sig[2] > upper:
            data = {
                "type": 'bullish',
                "value": sig[2],
                "index": sig[3],
                "date": sig[0]
            }
            signals_of_note.append(data)

        elif sig[2] < lower:
            data = {
                "type": 'bearish',
                "value": sig[2],
                "index": sig[3],
                "date": sig[0]
            }
            signals_of_note.append(data)

    return signals_of_note
