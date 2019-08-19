import pandas as pd 
import numpy as np 
from scipy.stats import linregress

def linear_regression(x_list, y_list) -> list:
    """ returns [m_slope, intercept] """
    x = np.array(x_list)
    y = np.array(y_list)

    n = np.size(x)
    m_x = np.mean(x)
    m_y = np.mean(y)
    SS_xy = np.sum(y * x) - (n * m_y * m_x)
    SS_xx = np.sum(x * x) - (n * m_x * m_x)

    m_slope = SS_xy / SS_xx
    intercept = m_y - (m_slope * m_x)

    return [m_slope, intercept]



def local_minima(pricing) -> list:
    """ returns: minimas = [traded_day, value] """
    pricing = list(pricing)

    minimas = []
    dropping = False
    min_val = pricing[0]
    min_ind = 0

    for pt in range(len(pricing)):
        
        if dropping == False:
            if (pricing[pt] < min_val):
                dropping = True

            min_val = pricing[pt]
            min_ind = pt 

        else: 
            if (pricing[pt] > min_val):
                minimas.append([min_ind, min_val])
                dropping = False 

            min_ind = pt 
            min_val = pricing[pt]

    return minimas         


def lower_low(data, start_val, start_ind) -> list:
    """ Looks for a bounce (rise) then lower low """
    data = list(data)
    track_ind = start_ind 
    track_val = start_val 

    # 0: first descent or rise; 1: lower low (in progress); 2: rise (lowest low found/not found)
    bounce_state = 0 
    lows = []

    for price in range(start_ind, len(data)):

        if (data[price] < start_val) and (bounce_state < 2):
            track_ind = price 
            track_val = data[price]
            bounce_state = 1

        if (data[price] > track_val) and (bounce_state == 1):
            bounce_state = 2

        if (data[price] < track_val) and (bounce_state > 1):
            bounce_state = 3
            track_ind = price 
            track_val = data[price]

        if (data[price] > track_val) and (bounce_state == 3):
            bounce_state = 4
            lows.append([track_val, track_ind])
            

    return lows 


def higher_high(data, start_val, start_ind) -> list:
    """ Looks for a bounce (rise) then lower low """
    data = list(data)
    track_ind = start_ind 
    track_val = start_val 

    # 0: first descent or rise; 1: lower low (in progress); 2: rise (lowest low found/not found)
    bounce_state = 0 
    highs = []

    for price in range(start_ind, len(data)):

        if (data[price] > start_val) and (bounce_state < 2):
            track_ind = price 
            track_val = data[price]
            bounce_state = 1

        if (data[price] < track_val) and (bounce_state == 1):
            bounce_state = 2

        if (data[price] > track_val) and (bounce_state > 1):
            bounce_state = 3
            track_ind = price 
            track_val = data[price]

        if (data[price] < track_val) and (bounce_state == 3):
            bounce_state = 4
            highs.append([track_val, track_ind])
            

    return highs 


def bull_bear_th(osc, start, thresh, bull_bear='bull'):
    count = start
    if bull_bear == 'bull':
        while count < len(osc):
            if osc[count] > thresh:
                return count
            count += 1

    if bull_bear == 'bear':
        while count < len(osc):
            if osc[count] < thresh:
                return count
            count += 1

    return None 


def beta_comparison(fund: pd.DataFrame, benchmark: pd.DataFrame) -> float:
    tot_len = len(fund['Close'])
    if pd.isna(fund['Close'][len(fund['Close'])-1]):
        tot_len -= 1

    fund_return = []
    fund_return.append(0.0)
    bench_return = []
    bench_return.append(0.0)
    for i in range(1,tot_len):
        ret = (fund['Close'][i]-fund['Close'][i-1]) / fund['Close'][i-1] * 100.0
        fund_return.append(ret)
        ret = (benchmark['Close'][i]-benchmark['Close'][i-1]) / benchmark['Close'][i-1] * 100.0
        bench_return.append(ret)

    # slope, intercept, r-correlation, p-value, stderr
    beta_figures = linregress(bench_return, fund_return)
    rsqd = beta_figures[2]**2
    
    return beta_figures[0], rsqd

