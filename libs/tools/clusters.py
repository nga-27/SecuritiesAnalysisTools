import pandas as pd 
import numpy as np 

from libs.utils import dual_plotting # nasit_cluster_signal, nasit_cluster_score

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
            dates.append([fund.index[i], fund['Close'][i], cluster_list[i], i])
    return dates 


def generate_cluster(position: pd.DataFrame, function: str) -> list:
    """ subfunction to do clustering (removed from main for flexibility) """
    clusters = []

    for i in range(len(position)):
        clusters.append(0)

    if function == 'full_stochastic':
        fast = full_stochastic(position, config=[10,3,3], plot_output=False)
        med = full_stochastic(position, config=[14,3,3], plot_output=False)
        slow = full_stochastic(position, config=[20,5,5], plot_output=False)
    elif function == 'ultimate':
        fast = ultimate_oscillator(position, config=[4,8,16], plot_output=False)
        med = ultimate_oscillator(position, config=[5,10,20], plot_output=False)
        slow = ultimate_oscillator(position, config=[7,14,28], plot_output=False)
    elif function == 'rsi':
        fast = RSI(position, plot_output=False, period=8)
        med = RSI(position, plot_output=False, period=14)
        slow = RSI(position, plot_output=False, period=20)
    elif function == 'all':
        fast = full_stochastic(position, config=[10,3,3], plot_output=False)
        med = full_stochastic(position, config=[14,3,3], plot_output=False)
        slow = full_stochastic(position, config=[20,5,5], plot_output=False)
        fastu = ultimate_oscillator(position, config=[4,8,16], plot_output=False)
        medu = ultimate_oscillator(position, config=[5,10,20], plot_output=False)
        slowu = ultimate_oscillator(position, config=[7,14,28], plot_output=False)
        fastr = RSI(position, plot_output=False, period=8)
        medr = RSI(position, plot_output=False, period=14)
        slowr = RSI(position, plot_output=False, period=20)
    else:
        print(f'Warning: Unrecognized function input of {function} in cluster_oscs.')
        return None
    
    if function == 'all':
        clusters = clustering(clusters, fast, weight=1)
        clusters = clustering(clusters, med, weight=2)
        clusters = clustering(clusters, slow, weight=2)
        clusters = clustering(clusters, fastr, weight=2)
        clusters = clustering(clusters, medr, weight=4)
        clusters = clustering(clusters, slowr, weight=3)
        clusters = clustering(clusters, fastu, weight=1)
        clusters = clustering(clusters, medu, weight=3)
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


def cluster_oscs(position: pd.DataFrame, name='', plot_output=True, function: str='full_stochastic', filter_thresh=7) -> dict:
    """ 2-3-5-8 multiplier comparing several different osc lengths """
    cluster_oscs = {}
    
    clusters = generate_cluster(position, function)

    #clusters_filtered = cluster_filtering(clusters, filter_thresh)
    clusters_wma = windowed_ma_list(clusters, interval=3)
    dates = cluster_dates(clusters_wma, position) 
    cluster_oscs[function] = dates

    #nasit_signal = nasit_cluster_signal(clusters)
    #cluster_oscs['nasit'] = nasit_cluster_score(clusters)
    
    if plot_output:
        name = name + ' - ' + function
        dual_plotting(position['Close'], clusters, 'price', 'clustered oscillator', 'trading days', title=name)
        dual_plotting(position['Close'], clusters_wma, 'price', 'clustered oscillator', 'trading days', title=name)
        #dual_plotting(position['Close'], nasit_signal, 'price', 'clustered nasit', 'trading days', title=name)

    return clusters_wma, cluster_oscs
