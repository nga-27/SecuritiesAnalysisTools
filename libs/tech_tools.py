import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import os 

from .linear_regression import dual_plotting, higher_high, lower_low, bull_bear_th
from .sat_utils import  name_parser
from .rsi_tools import generate_rsi_signal, determine_rsi_swing_rejection
from .ult_osc_tools import generate_ultimate_osc_signal, ult_osc_find_triggers, ult_osc_output
from .cluster_tools import clustering, cluster_filtering
from .full_stoch_tools import generate_full_stoch_signal, get_full_stoch_features
from .trend_tools import get_trend, get_trend_analysis
from .relative_strength import normalized_ratio, period_strength


def full_stochastic(position: pd.DataFrame, name='', config: list=[14, 3, 3], plot_output=True) -> dict:
    """ During a trend, increase config to avoid false signals:
        ex: downtrend, larger config will minimize false 'overbought' readings

        position:
            pd.DataFrame - ['Date', 'Open', 'Close', 'High', 'Low', 'Adj Close']

        typical configs: [14,3,3], [10,3,3], [20, 5, 5]
    """

    feature_list = generate_full_stoch_signal(position, config=config) 

    stochastic, full_stoch = get_full_stoch_features(position, feature_list)
            
    if plot_output:
        dual_plotting(position['Close'], stochastic, 'Position Price', 'Oscillator Signal', title=name)

    return full_stoch



def ultimate_oscillator(position: pd.DataFrame, name='', config: list=[7, 14, 28], plot_output=True) -> dict:
    """ Ultimate stoch: [(4 * Avg7 ) + (2 * Avg14) + (1 * Avg28)] / 7

            Avg(x) = BP(x) / TR(x)
            BP(x) = sum(close - floor[period low OR prior close]) for x days
            TR(x) = sum()
    """
    stats = position
    ult_osc = generate_ultimate_osc_signal(stats, config=config)

    trigger = ult_osc_find_triggers(stats, ult_osc)

    plots, ultimate = ult_osc_output(trigger, len(stats['Close']))
    ultimate['tabular'] = ult_osc

    if plot_output:
        dual_plotting(stats['Close'], ult_osc, 'price', 'ultimate oscillator', 'trading days', title=name)
        dual_plotting(stats['Close'], plots, 'price', 'buy-sell signal', 'trading days', title=name)

    return ultimate



def trend_filter(osc: dict, position: pd.DataFrame) -> dict:
    """ Filters oscillator dict to remove trend bias.

        Ex: strong upward trend -> removes weaker drops in oscillators
    """
    filtered = {}

    return filtered 



def cluster_oscs(position: pd.DataFrame, name='', plot_output=True, function: str='full_stochastic', filter_thresh=7) -> list:
    """ 2-3-5-8 multiplier comparing several different osc lengths """
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
        fast1 = ultimate_oscillator(position, config=[4,8,16], plot_output=False)
        med1 = ultimate_oscillator(position, config=[5,10,20], plot_output=False)
        slow1 = ultimate_oscillator(position, config=[7,14,28], plot_output=False)
        fast2 = RSI(position, plot_output=False, period=8)
        med2 = RSI(position, plot_output=False, period=14)
        slow2 = RSI(position, plot_output=False, period=20)
    else:
        print(f'Warning: Unrecognized function input of {function} in cluster_oscs.')
        return None

    clusters = clustering(clusters, fast)
    clusters = clustering(clusters, med)
    clusters = clustering(clusters, slow)
    
    if function == 'all':
        clusters = clustering(clusters, fast1)
        clusters = clustering(clusters, med1)
        clusters = clustering(clusters, slow1)
        clusters = clustering(clusters, fast2)
        clusters = clustering(clusters, med2)
        clusters = clustering(clusters, slow2)

    clusters = cluster_filtering(clusters, filter_thresh)
    
    if plot_output:
        dual_plotting(position['Close'], clusters, 'price', 'clustered oscillator', 'trading days', title=name)

    return clusters 



def RSI(position: pd.DataFrame, name='', plot_output=True, period: int=14) -> dict:
    """ Relative Strength Indicator """
    RSI = generate_rsi_signal(position, period=period)

    plotting, rsi_swings = determine_rsi_swing_rejection(position, RSI)
    rsi_swings['tabular'] = RSI

    if plot_output:
        dual_plotting(position['Close'], RSI, 'price', 'RSI', 'trading days', title=name)
        dual_plotting(position['Close'], plotting, 'price', 'RSI indicators', 'trading days', title=name)
       

    # TODO: conditions of rsi (divergence, etc.)

    return rsi_swings



def relative_strength(positionA: pd.DataFrame, positionB: pd.DataFrame, sector: str='', plot_output=True):
    rat = normalized_ratio(positionA, positionB)
    st = period_strength(positionA, periods=[20, 50, 100], sector=sector)
    
    if plot_output:
        plt.plot(rat)
        plt.show()

    return st 