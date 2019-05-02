import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

TREND_PTS = [2, 3, 6]

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



def dual_plotting(y1: list, y2: list, y1_label: str, y2_label: str, x_label: str='trading days', title=''):
    fig, ax1 = plt.subplots()
    color = 'tab:orange'
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y1_label, color=color)
    ax1.plot(y1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(linestyle=':')
    plt.legend([y1_label])

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel(y2_label, color=color)
    ax2.plot(y2, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid()

    fig.tight_layout()
    plt.legend([y2_label])
    if len(title) > 0:
        plt.title(title)
    plt.show()


def resistance(highs) -> list:
    highs = list(highs)
    if len(highs) <= 14:
        points = TREND_PTS[1]
    elif len(highs) <= 28:
        points = TREND_PTS[2]
    else:
        points = TREND_PTS[0]

    sortedList = sorted(highs, reverse=True)
    
    refs = []
    indices = []
    for i in range(points):
        refs.append(sortedList[i])
        indices.append(highs.index(refs[i]))
    
    trendslope = linear_regression(indices, refs)
    resistance_level = trendslope[1] + trendslope[0] * len(highs)

    return [trendslope, resistance_level]


def support(lows) -> list:
    lows = list(lows)
    if len(lows) <= 14:
        points = TREND_PTS[1]
    elif len(lows) <= 28:
        points = TREND_PTS[2]
    else:
        points = TREND_PTS[0]

    sortedList = sorted(lows)
    
    refs = []
    indices = []
    for i in range(points):
        refs.append(sortedList[i])
        indices.append(lows.index(refs[i]))
    
    trendslope = linear_regression(indices, refs)
    resistance_level = trendslope[1] + trendslope[0] * len(lows)

    return [trendslope, resistance_level]


def trendline(resistance, support) -> list:
    trend_slope = (resistance[0][0] + support[0][0]) / 2.0
    intercept = (resistance[0][1] + support[0][1]) / 2.0
    final_val = intercept + trend_slope * len(resistance)
    difference = resistance[0][0] - support[0][0]

    return [[trend_slope, intercept], final_val, difference]


def trendline_deriv(price) -> list:
    price = list(price)
    derivative = []
    for val in range(1, len(price)):
        derivative.append(price[val] - price[val-1])

    deriv = np.sum(derivative)
    deriv = deriv / float(len(derivative))
    return deriv


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



