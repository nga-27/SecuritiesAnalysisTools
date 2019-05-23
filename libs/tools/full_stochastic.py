import pandas as pd 
import numpy as np 

from libs.utils import dual_plotting, date_extractor
#from libs.utils import nasit_oscillator_score, nasit_oscillator_signal 

def generate_full_stoch_signal(position: pd.DataFrame, config=[14, 3, 3]) -> list:
    """ Generates signal
    
    Returns:
        [k_smooth, d_sma] - features of full_stochastic signal

    """
    k_instant = []
    k_smooth = []
    d_sma = []

    for i in range(config[0]-1):
        k_instant.append(50.0)
        k_smooth.append(50.0)
        d_sma.append(50.0)

    for i in range(config[0]-1, len(position['Close'])):

        # Find first lookback of oscillator
        lows = position['Low'][i-(config[0]-1):i+1]
        highs = position['High'][i-(config[0]-1):i+1]
        low = np.min(lows)
        high = np.max(highs)

        s = [low, high, position['Close'][i]]

        K = (position['Close'][i] - low) / (high - low) * 100.0
        k_instant.append(K)

        # Smooth oscillator with config[1]
        k_smooth.append(np.average(k_instant[i-(config[1]-1):i+1]))

        # Find 'Simple Moving Average' (SMA) of k2
        d_sma.append(np.average(k_smooth[i-(config[2]-1):i+1]))

    return [k_smooth, d_sma] 


def get_full_stoch_features(position: pd.DataFrame, features: list) -> list:
    """ Converts signal features to conditions (divergence/convergence)

    Args:
        features -> [k_smooth, d_sma]

    Returns:
        [k_smooth, full_stoch (dict)] -> [signal_list, feature dict]
    """
    SELL_TH = 80.0
    BUY_TH = 20.0

    k_smooth = features[0]
    d_sma = features[1]

    full_stoch = {}
    full_stoch['bullish'] = []
    full_stoch['bearish'] = []
    full_stoch['tabular'] = k_smooth

    stochastic = []

    indicator = 0 # 0 is neutral, 1,2 is oversold, 3,4: is overbought
    for i in range(len(position['Close'])):

        if k_smooth[i] > SELL_TH:
            indicator = 3
            stochastic.append(0)
        elif (indicator == 3) and (k_smooth[i] < d_sma[i]):
            indicator = 4
            stochastic.append(0)
        elif (indicator == 4) and (k_smooth[i] < SELL_TH):
            indicator = 0
            full_stoch['bearish'].append([date_extractor(position.index[i], _format='str'), position['Close'][i], i])
            stochastic.append(1)

        elif k_smooth[i] < BUY_TH:
            indicator = 1
            stochastic.append(0)
        elif (indicator == 1) and (k_smooth[i] > d_sma[i]):
            indicator = 2
            stochastic.append(0)
        elif (indicator == 2) and (k_smooth[i] > BUY_TH):
            indicator = 0
            full_stoch['bullish'].append([date_extractor(position.index[i], _format='str'), position['Close'][i], i])
            stochastic.append(-1)

        else:
            stochastic.append(0)

    return [stochastic, full_stoch]



def full_stochastic(position: pd.DataFrame, name='', config: list=[14, 3, 3], plot_output=True, out_suppress=True) -> dict:
    """ During a trend, increase config to avoid false signals:
        ex: downtrend, larger config will minimize false 'overbought' readings

        position:
            pd.DataFrame - ['Date', 'Open', 'Close', 'High', 'Low', 'Adj Close']

        typical configs: [14,3,3], [10,3,3], [20, 5, 5]
    """

    feature_list = generate_full_stoch_signal(position, config=config) 

    stochastic, full_stoch = get_full_stoch_features(position, feature_list)
    
    #nasit_signal = nasit_oscillator_signal(full_stoch, stochastic)
    #full_stoch['nasit'] = nasit_oscillator_score(full_stoch, stochastic)

    if not out_suppress:
        name2 = name + ' - Stochastic'
        if plot_output:
            dual_plotting(position['Close'], stochastic, 'Position Price', 'Oscillator Signal', title=name2)
            #dual_plotting(position['Close'], nasit_signal, 'Position Price', 'Oscillator Signal', title='nasit_stoch')
        else:
            filename = name +'/stochastic_{}.png'.format(name)
            dual_plotting(position['Close'], stochastic, 'Position Price', 'Stochastic Oscillator', 'Trading Days', title=name2, saveFig=True, filename=filename)

    return full_stoch
