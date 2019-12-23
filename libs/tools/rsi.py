import pandas as pd 
import numpy as np 

from libs.utils import dual_plotting, date_extractor, SP500


def generate_rsi_signal(position: pd.DataFrame, period: int=14, p_bar=None) -> list:
    """ Generates a list of relative strength indicators """
    PERIOD = period
    change = []
    change.append(0.0)
    for i in range(1, len(position['Close'])):
        per = (position['Close'][i] - position['Close'][i-1]) / position['Close'][i-1] * 100.0
        change.append(np.round(per, 6))

    if p_bar is not None: p_bar.uptick(increment=0.15)

    RSI = []
    # gains, losses, rs
    RS = []

    for i in range(0, PERIOD):
        RSI.append(50.0)
        RS.append([0.0, 0.0, 1.0])

    # Calculate RS for all future points
    for i in range(PERIOD, len(change)):
        pos = 0.0
        neg = 0.0
        for j in range(i-PERIOD, i):
            if change[j] > 0.0:
                pos += change[j]
            else:
                neg += np.abs(change[j])
        
        if i == PERIOD:
            if neg == 0.0:
                rs = float('inf')
            else:
                rs = np.round(pos / neg, 6)
            RS.append([np.round(pos/float(PERIOD), 6), np.round(neg/float(PERIOD), 6), rs])
        else:
            if change[i] > 0.0:
                if RS[i-1][1] == 0.0:
                    rs = float('inf')
                else: 
                    rs = (((RS[i-1][0] * float(PERIOD-1)) + change[i]) / float(PERIOD)) / (((RS[i-1][1] * float(PERIOD-1)) + 0.0) / float(PERIOD))
            else:
                if RS[i-1][1] == 0.0:
                    rs = float('inf')
                else:
                    rs = (((RS[i-1][0] * float(PERIOD-1)) + 0.00) / float(PERIOD)) / (((RS[i-1][1] * float(PERIOD-1)) + np.abs(change[i])) / float(PERIOD))

            RS.append([np.round(pos/float(PERIOD), 6), np.round(neg/float(PERIOD), 6), rs])

        rsi = 100.0 - (100.0 / (1.0 + RS[i][2]))
        RSI.append(np.round(rsi, 6))

    if p_bar is not None: p_bar.uptick(increment=0.15)
    
    return RSI



def determine_rsi_swing_rejection(position: pd.DataFrame, rsi_signal: list, p_bar=None) -> dict:
    """ Find bullish / bearish and RSI indicators:

        1. go beyond threshold
        2. go back within thresholds
        3. have local minima/maxima inside thresholds
        4. exceed max/min (bull/bear) of previous maxima/minima
    """

    LOW_TH = 30.0
    HIGH_TH = 70.0

    swings = {}
    swings['bullish'] = []
    swings['bearish'] = []
    indicator = []

    increment = 0.3 / float(len(rsi_signal))

    state = 0
    minima = 0.0
    maxima = 0.0
    for i in range(len(rsi_signal)):
        
        if (state == 0) and (rsi_signal[i] < LOW_TH):
            # Start of a bullish signal
            state = 1
            indicator.append(0.0)
        elif (state == 1) and (rsi_signal[i] > LOW_TH):
            state = 2
            maxima = rsi_signal[i]
            indicator.append(0.0)
        elif (state == 2):
            if rsi_signal[i] >= maxima:
                maxima = rsi_signal[i]
            else:
                minima = rsi_signal[i]
                state = 3
            indicator.append(0.0)
        elif (state == 3):
            if rsi_signal[i] < LOW_TH:
                # Failed attempted breakout
                state = 1
            if rsi_signal[i] < minima:
                minima = rsi_signal[i]
            else:
                state = 4
            indicator.append(0.0)
        elif (state == 4):
            if rsi_signal[i] > maxima:
                # Have found a bullish breakout!
                swings['bullish'].append([date_extractor(position.index[i], _format='str'), position['Close'][i], i])
                state = 0
                minima = 0.0
                maxima = 0.0 
                indicator.append(-1.0)
            else:
                indicator.append(0.0)


        elif (state == 0) and (rsi_signal[i] > HIGH_TH):
            state = 5
            indicator.append(0.0)
        elif (state == 5) and (rsi_signal[i] < HIGH_TH):
            state = 6
            minima = rsi_signal[i]
            indicator.append(0.0)
        elif (state == 6):
            if rsi_signal[i] <= minima:
                minima = rsi_signal[i]
            else:
                maxima = rsi_signal[i]
                state = 7
            indicator.append(0.0)
        elif (state == 7):
            if rsi_signal[i] > HIGH_TH:
                # Failed attempted breakout
                state = 5
            if rsi_signal[i] > maxima:
                maxima = rsi_signal[i]
            else:
                state = 8
            indicator.append(0.0)
        elif (state == 8):
            if rsi_signal[i] < minima:
                swings['bearish'].append([date_extractor(position.index[i], _format='str'), position['Close'][i], i])
                state = 0
                minima = 0.0
                maxima = 0.0
                indicator.append(1.0)
            else:
                indicator.append(0.0)

        else:
            indicator.append(0.0)

        if p_bar is not None: p_bar.uptick(increment=increment)

    return [indicator, swings]


def over_threshold_lists(overbought: float, oversold: float, fund_length: int) -> dict:
    ovbt = []
    ovsld = []
    for _ in range(fund_length):
        ovbt.append(overbought)
        ovsld.append(oversold)
    over_th = {"overbought": ovbt, "oversold": ovsld}
    return over_th


def RSI(position: pd.DataFrame, **kwargs) -> dict: 
    """
    Relative Strength Indicator

    args:
        position:       (pd.DataFrame) list of y-value datasets to be plotted (multiple)

    optional args:
        name:           (list) name of fund, primarily for plotting; DEFAULT=''
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        period:         (int) size of RSI indicator; DEFAULT=14 
        out_suppress:   (bool) output plot/prints are suppressed; DEFAULT=True
        progress_bar:   (ProgressBar) DEFAULT=None
        overbought:     (float) threshold to trigger overbought/sell condition; DEFAULT=70.0
        oversold:       (float) threshold to trigger oversold/buy condition; DEFAULT=30.0
        auto_trend:     (bool) True calculates basic trend, applies to thresholds; DEFAULT=True

    returns:
        rsi_swings:     (dict) contains all rsi information
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    period = kwargs.get('period', 14)
    out_suppress = kwargs.get('out_suppress', True)
    progress_bar = kwargs.get('progress_bar', None)
    overbought = kwargs.get('overbought', 70.0)
    oversold = kwargs.get('oversold', 30.0)
    auto_trend = kwargs.get('auto_trend', True)

    RSI = generate_rsi_signal(position, period=period, p_bar=progress_bar)

    plotting, rsi_swings = determine_rsi_swing_rejection(position, RSI, p_bar=progress_bar)
    rsi_swings['tabular'] = RSI
    rsi_swings['thresholds'] = {"overbought": overbought, "oversold": oversold}

    over_thresholds = over_threshold_lists(overbought, oversold, len(position['Close']))
    main_plots = [RSI, over_thresholds['overbought'], over_thresholds['oversold']]

    if not out_suppress:
        name3 = SP500.get(name, name)
        name2 = name3 + ' - RSI'
        if plot_output:
            dual_plotting(position['Close'], main_plots, 'Position Price', 'RSI', title=name2)
            dual_plotting(position['Close'], plotting, 'Position Price', 'RSI Indicators', title=name2)
        else:
            filename1 = name + '/RSI_standard_{}.png'.format(name)
            filename2 = name + '/RSI_indicator_{}.png'.format(name)
            dual_plotting(  position['Close'], main_plots, 'Position Price', 'RSI', 
                            title=name2, saveFig=True, filename=filename1)
            dual_plotting(  position['Close'], plotting, 'Position Price', 'RSI Indicators', 
                            title=name2, saveFig=True, filename=filename2)

    if progress_bar is not None: progress_bar.uptick(increment=0.4)
        
    return rsi_swings
