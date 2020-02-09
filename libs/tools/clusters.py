import pandas as pd
import numpy as np

from libs.utils import dual_plotting, date_extractor, ProgressBar, SP500

from .ultimate_oscillator import ultimate_oscillator
from .rsi import RSI
from .full_stochastic import full_stochastic

from .moving_average import windowed_moving_avg
from .trends import autotrend

BASE_WEIGHTS = {
    'stoch': 2,
    'rsi': 3,
    'ultimate': 7
}


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
    dates = []
    for i in range(len(cluster_list)):
        if cluster_list[i] != 0:
            dates.append([date_extractor(fund.index[i], _format='str'),
                          fund['Close'][i], cluster_list[i], i])
    return dates


def generate_cluster(position: pd.DataFrame, function: str, name='', p_bar=None) -> list:
    """ subfunction to do clustering (removed from main for flexibility) """
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
            position, config=[5, 10, 20], plot_output=False, name=name)
        slow = ultimate_oscillator(
            position, config=[7, 14, 28], plot_output=False, name=name)

    elif function == 'rsi':
        fast = RSI(position, plot_output=False, period=8, name=name)
        med = RSI(position, plot_output=False, period=14, name=name)
        slow = RSI(position, plot_output=False, period=20)

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
        fast_rsi = RSI(position, plot_output=False, period=8, name=name)
        med_rsi = RSI(position, plot_output=False, period=14, name=name)
        slow_rsi = RSI(position, plot_output=False, period=20, name=name)

    elif function == 'market':
        fast = full_stochastic(
            position, config=[14, 3, 3], plot_output=False, name=name)
        med = ultimate_oscillator(
            position, config=[5, 10, 20], plot_output=False, name=name)
        slow = RSI(position, plot_output=False, period=14, name=name)

    else:
        print(
            f'Warning: Unrecognized function input of {function} in cluster_oscs.')
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
    """ Using trend slopes, will assign slightly different weights to each oscillator """

    types = kwargs.get('types', ['stoch', 'rsi', 'ultimate'])
    speeds = kwargs.get('speeds', ['fast', 'medium', 'slow'])
    trend = autotrend(position['Close'], periods=[28, 56, 84], weights=[
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


def cluster_oscs(position: pd.DataFrame, **kwargs):
    """
    2-3-5-8 multiplier comparing several different osc lengths

    args:
        position:       (pd.DataFrame) list of y-value datasets to be plotted (multiple)

    optional args:
        name:           (list) name of fund, primarily for plotting; DEFAULT=''
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        function:       (str) type of oscillator; DEFAULT='full_stochastic' 
                                (others: ultimate, rsi, all, market)
        wma:            (bool) output signal is filtered by windowed moving average; DEFAULT=True
        progress_bar:   (ProgressBar) DEFAULT=None

    returns:
        cluster_oscs:   (dict) contains all clustered oscillator informatio
        clusters:       (list) clustered oscillator signal
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    function = kwargs.get('function', 'full_stochastic')
    wma = kwargs.get('wma', True)
    prog_bar = kwargs.get('progress_bar', None)

    cluster_oscs = {}

    clusters = generate_cluster(position, function, p_bar=prog_bar)

    #clusters_filtered = cluster_filtering(clusters, filter_thresh)
    clusters_wma = windowed_moving_avg(clusters, interval=3, data_type='list')
    if prog_bar is not None:
        prog_bar.uptick(increment=0.1)

    dates = cluster_dates(clusters_wma, position)
    if prog_bar is not None:
        prog_bar.uptick(increment=0.2)

    cluster_oscs['clustered type'] = function
    cluster_oscs[function] = dates

    name3 = SP500.get(name, name)
    name2 = name3 + ' - Clustering: ' + function
    if plot_output:
        dual_plotting(position['Close'], clusters, 'Position Price',
                      'Clustered Oscillator', x_label='Trading Days', title=name2)
        #dual_plotting(position['Close'], clusters_wma, 'price', 'clustered oscillator', 'trading days', title=name)
    else:
        filename = name + '/clustering_{}_{}.png'.format(name, function)
        dual_plotting(y1=position['Close'], y2=clusters, y1_label='Price', y2_label='Clustered Oscillator',
                      x_label='Trading Days', title=name2, saveFig=True, filename=filename)

    if prog_bar is not None:
        prog_bar.uptick(increment=0.2)

    if wma:
        return clusters_wma, cluster_oscs
    else:
        return clusters, cluster_oscs
