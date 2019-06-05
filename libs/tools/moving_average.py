import pandas as pd 
import numpy as np 

def exponential_ma(fund: pd.DataFrame, interval: int) -> list:
    ema = []
    k = 2.0 / (float(interval) + 1.0)
    for i in range(interval-1):
        ema.append(fund['Close'][i])
    for i in range(interval-1, len(fund['Close'])):
        ema.append(np.mean(fund['Close'][i-(interval-1):i+1]))
        if i != interval-1:
            ema[i] = ema[i-1] * (1.0 - k) + fund['Close'][i] * k

    return ema 


def exponential_ma_list(item: list, interval: int) -> list:
    ema = []
    k = 2.0 / (float(interval) + 1.0)
    if len(item) > interval:
        for i in range(interval-1):
            ema.append(item[i])
        for i in range(interval-1, len(item)):
            ema.append(np.mean(item[i-(interval-1):i+1]))
            if i != interval-1:
                ema[i] = ema[i-1] * (1.0 - k) + item[i] * k
    else:
        ema = item

    return ema 


def windowed_ma_list(item: list, interval: int) -> list:
    left = int(np.floor(float(interval) / 2))
    wma = []
    for i in range(left):
        wma.append(item[i])
    for i in range(left, len(item)-left):
        wma.append(np.mean(item[i-(left):i+1+(left)]))
    for i in range(len(item)-left, len(item)):
        wma.append(item[i])

    return wma 


def simple_ma_list(item: list, interval: int) -> list:
    ma = []
    for i in range(interval-1):
        ma.append(item[i])
    for i in range(interval-1, len(item)):
        av = np.mean(item[i-(interval-1):i+1])
        ma.append(av)

    return ma 



def triple_moving_average(fund: pd.DataFrame, config=[12, 50, 200], plot_output=True, name='') -> list:
    from libs.utils import generic_plotting

    tshort = []
    tmed = []
    tlong = []

    tot_len = len(fund['Close'])

    for i in range(config[0]):
        tshort.append(fund['Close'][i])
        tmed.append(fund['Close'][i])
        tlong.append(fund['Close'][i])
    for i in range(config[0], config[1]):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(fund['Close'][i])
        tlong.append(fund['Close'][i])
    for i in range(config[1], config[2]):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(np.mean(fund['Close'][i-config[1]:i+1]))
        tlong.append(fund['Close'][i])
    for i in range(config[2], tot_len):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(np.mean(fund['Close'][i-config[1]:i+1]))
        tlong.append(np.mean(fund['Close'][i-config[2]:i+1]))

    name2 = name + ' - Simple Moving Averages [{}, {}, {}]'.format(config[0], config[1], config[2])
    legend = ['Price', f'{config[0]}-SMA', f'{config[1]}-SMA', f'{config[2]}-SMA']
    if plot_output:
        generic_plotting([fund['Close'], tshort, tmed, tlong], legend=legend, title=name2)
    else:
        filename = name +'/simple_moving_averages_{}.png'.format(name)
        generic_plotting([fund['Close'], tshort, tmed, tlong], legend=legend, title=name2, saveFig=True, filename=filename)

    return tshort, tmed, tlong



def triple_exp_mov_average(fund: pd.DataFrame, config=[9, 13, 50], plot_output=True, name='') -> list:
    from libs.utils import generic_plotting

    tshort = exponential_ma(fund, config[0])
    tmed = exponential_ma(fund, config[1])
    tlong = exponential_ma(fund, config[2])

    name2 = name + ' - Exp Moving Averages [{}, {}, {}]'.format(config[0], config[1], config[2])
    legend = ['Price', f'{config[0]}-EMA', f'{config[1]}-EMA', f'{config[2]}-EMA']
    if plot_output:
        generic_plotting([fund['Close'], tshort, tmed, tlong], legend=legend, title=name2)
    else:
        filename = name +'/exp_moving_averages_{}.png'.format(name)
        generic_plotting([fund['Close'], tshort, tmed, tlong], legend=legend, title=name2, saveFig=True, filename=filename)

    return tshort, tmed, tlong


def moving_average_swing_trade(fund: pd.DataFrame, function: str='ema', config=[], plot_output=True, name=''):
    """ can output details later """
    from libs.utils import specialty_plotting

    swings = []
    # TODO: utilize 'function' feature
    if config == []:
        sh, me, ln = triple_exp_mov_average(fund, plot_output=False, name=name)
    else:
        sh, me, ln = triple_exp_mov_average(fund, config=config, plot_output=False, name=name)

    prev_state = 3
    hold = 'none'
    for i in range(len(sh)):
        state, hold = state_management(fund['Close'][i], sh[i], me[i], ln[i], prev_state, hold=hold)
        if state == 1:
            # Bullish Reversal
            swings.append(-2.0)
        elif state == 5:
            # Bearish Reversal
            swings.append(2.0)
        elif state == 7:
            swings.append(-1.0)
        elif state == 8:
            swings.append(1.0)
        elif state == 2:
            swings.append(0.5)
        elif state == 4:
            swings.append(-0.5)
        else:
            swings.append(0.0)
        prev_state = state

    name2 = name + ' - Swing Trade EMAs'
    legend = ['Price', 'Short-EMA', 'Medium-EMA', 'Long-EMA', 'Swing Signal']
    if plot_output:
        specialty_plotting([fund['Close'], sh, me, ln, swings], alt_ax_index=[4] , legend=legend, title=name2)
    else:
        filename = name +'/swing_trades_ema_{}.png'.format(name)
        specialty_plotting([fund['Close'], sh, me, ln, swings], alt_ax_index=[4] , legend=['Swing Signal'], title=name2, saveFig=True, filename=filename)



def state_management(price: float, sht: float, med: float, lng: float, prev_state: int, hold='bull'):
    """ 
    states: bullish -> bearish; 
        0 - price > sht > med > lng (bullish)
        1 - sht > med > lng & prev_state = 2 (bullish reversal)
        2 - sht < med > lng (potential bearish start)
        3 - "other"
        4 - sht > med < lng (potential bullish start)
        5 - sht < med < lng & prev_state = 4 (bearish reversal)
        6 - price < sht < med < lng (bearish)
        ======
        7 - enter into bullish from non-full bullish
        8 - enter into bearish from non-full bearish
    """
    if ((sht > med) and (med > lng) and (prev_state == 2)):
        state =  1
    elif ((sht < med) and (med < lng) and (prev_state == 4)):
        state = 5
    elif ((sht < med) and (med > lng)):
        #hold = 'none'
        state = 2
    elif ((sht > med) and (med < lng)):
        #hold = 'none'
        state = 4
    elif ((price < sht) and (sht < med) and (med < lng) and (prev_state != 8) and (hold != 'bear')):
        hold = 'bear'
        state =  8
    elif ((price > sht) and (sht > med) and (med > lng) and (prev_state != 7) and (hold != 'bull')):
        hold = 'bull'
        state = 7
    elif ((price > sht) and (sht > med) and (med > lng)):
        hold = 'bull'
        state = 0
    elif ((price < sht) and (sht < med) and (med < lng)):
        hold = 'bear'
        state = 6
    else:
        hold = 'none'
        state = 3

    return state, hold

    