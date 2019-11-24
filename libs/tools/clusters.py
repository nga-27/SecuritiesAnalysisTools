import pandas as pd 
import numpy as np 

from libs.utils import dual_plotting, date_extractor, ProgressBar

from .ultimate_oscillator import ultimate_oscillator 
from .rsi import RSI
from .full_stochastic import full_stochastic
from .moving_average import windowed_ma_list

def clustering(updatable: list, evaluator: dict, weight: int=1) -> list:
    for bull in evaluator['bullish']:
        index = bull[2]
        updatable[index] += (-8*weight) if updatable[index] != 0 else -1
        if index < len(updatable)-1:
            updatable[index-1] += (-5*weight) if updatable[index-1] != 0 else 0
            updatable[index+1] += (-5*weight) if updatable[index+1] != 0 else 0
        if index < len(updatable)-2:
            updatable[index-2] += (-3*weight) if updatable[index-2] != 0 else 0
            updatable[index+2] += (-3*weight) if updatable[index+2] != 0 else 0
        if index < len(updatable)-3:
            updatable[index-3] += (-2*weight) if updatable[index-3] != 0 else 0
            updatable[index+3] += (-2*weight) if updatable[index+3] != 0 else 0

    for bear in evaluator['bearish']:
        index = bear[2]
        updatable[index] += (8*weight) if updatable[index] != 0 else 1
        if index < len(updatable)-1:
            updatable[index-1] += (5*weight) if updatable[index-1] != 0 else 0
            updatable[index+1] += (5*weight) if updatable[index+1] != 0 else 0
        if index < len(updatable)-2:
            updatable[index-2] += (3*weight) if updatable[index-2] != 0 else 0
            updatable[index+2] += (3*weight) if updatable[index+2] != 0 else 0
        if index < len(updatable)-3:
            updatable[index-3] += (2*weight) if updatable[index-3] != 0 else 0
            updatable[index+3] += (2*weight) if updatable[index+3] != 0 else 0

    return updatable



def cluster_filtering(cluster_list: list, filter_thresh: int=7) -> list:
    """ Filters a clustered projection such that any x for (-filter_thresh < f[x] < filter_thresh) = 0 """
    for i in range(len(cluster_list)):
        if (cluster_list[i] < filter_thresh) and (cluster_list[i] > -filter_thresh):
            cluster_list[i] = 0

    return cluster_list



def cluster_dates(cluster_list: list, fund: pd.DataFrame) -> list:
    dates = []
    for i in range(len(cluster_list)):
        if cluster_list[i] != 0:
            dates.append([date_extractor(fund.index[i], _format='str'), fund['Close'][i], cluster_list[i], i])
    return dates 


def generate_cluster(position: pd.DataFrame, function: str, name='') -> list:
    """ subfunction to do clustering (removed from main for flexibility) """
    clusters = []

    for i in range(len(position)):
        clusters.append(0)

    if function == 'full_stochastic':
        fast = full_stochastic(position, config=[10,3,3], plot_output=False, name=name)
        med = full_stochastic(position, config=[14,3,3], plot_output=False, name=name)
        slow = full_stochastic(position, config=[20,5,5], plot_output=False, name=name)

    elif function == 'ultimate':
        fast = ultimate_oscillator(position, config=[4,8,16], plot_output=False, name=name)
        med = ultimate_oscillator(position, config=[5,10,20], plot_output=False, name=name)
        slow = ultimate_oscillator(position, config=[7,14,28], plot_output=False, name=name)

    elif function == 'rsi':
        fast = RSI(position, plot_output=False, period=8, name=name)
        med = RSI(position, plot_output=False, period=14, name=name)
        slow = RSI(position, plot_output=False, period=20)

    elif function == 'all':
        fast = full_stochastic(position, config=[10,3,3], plot_output=False, name=name)
        med = full_stochastic(position, config=[14,3,3], plot_output=False, name=name)
        slow = full_stochastic(position, config=[20,5,5], plot_output=False, name=name)
        fastu = ultimate_oscillator(position, config=[4,8,16], plot_output=False, name=name)
        medu = ultimate_oscillator(position, config=[5,10,20], plot_output=False, name=name)
        slowu = ultimate_oscillator(position, config=[7,14,28], plot_output=False, name=name)
        fastr = RSI(position, plot_output=False, period=8, name=name)
        medr = RSI(position, plot_output=False, period=14, name=name)
        slowr = RSI(position, plot_output=False, period=20, name=name)

    elif function == 'market':
        fast = full_stochastic(position, config=[14,3,3], plot_output=False, name=name)
        med = ultimate_oscillator(position, config=[5,10,20], plot_output=False, name=name)
        slow = RSI(position, plot_output=False, period=14, name=name)

    else:
        print(f'Warning: Unrecognized function input of {function} in cluster_oscs.')
        return None
    
    if function == 'all':
        clusters = clustering(clusters, fast, weight=1)
        clusters = clustering(clusters, med, weight=2)
        clusters = clustering(clusters, slow, weight=2)
        clusters = clustering(clusters, fastr, weight=2)
        clusters = clustering(clusters, medr, weight=5)
        clusters = clustering(clusters, slowr, weight=3)
        clusters = clustering(clusters, fastu, weight=1)
        clusters = clustering(clusters, medu, weight=2)
        clusters = clustering(clusters, slowu, weight=2)
    else:
        clusters = clustering(clusters, fast)
        clusters = clustering(clusters, med)
        clusters = clustering(clusters, slow)

    return clusters


def export_cluster_nasit_signal(position: pd.DataFrame, function: str='full_stochastic') -> list:
    clusters = generate_cluster(position, function)
    #nasit_signal = nasit_cluster_signal(clusters)
    return clusters


def cluster_oscs(   position: pd.DataFrame, 
                    name='', 
                    plot_output=True, 
                    function: str='full_stochastic', 
                    filter_thresh=7, 
                    wma=True,
                    prog_bar: ProgressBar=None) -> dict:
    """ 2-3-5-8 multiplier comparing several different osc lengths """
    cluster_oscs = {}
    
    clusters = generate_cluster(position, function)
    if prog_bar is not None: prog_bar.uptick(increment=0.5)

    #clusters_filtered = cluster_filtering(clusters, filter_thresh)
    clusters_wma = windowed_ma_list(clusters, interval=3)
    dates = cluster_dates(clusters_wma, position) 
    cluster_oscs['clustered type'] = function
    cluster_oscs[function] = dates
    
    name2 = name + ' - Clustering: ' + function
    if plot_output:
        dual_plotting(position['Close'], clusters, 'Position Price', 'Clustered Oscillator', 'Trading Days', title=name2)
        #dual_plotting(position['Close'], clusters_wma, 'price', 'clustered oscillator', 'trading days', title=name)
    else:
        filename = name + '/clustering_{}_{}.png'.format(name, function)
        dual_plotting(position['Close'], clusters, 'Price', 'Clustered Oscillator', 'Trading Days', title=name2, saveFig=True, filename=filename)

    if prog_bar is not None: prog_bar.uptick(increment=0.5)

    if wma:
        return clusters_wma, cluster_oscs
    else:
        return clusters, cluster_oscs
