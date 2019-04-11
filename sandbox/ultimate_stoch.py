import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from libs import linear_regression, dual_plotting, resistance, support, trendline
from libs import local_minima, trendline_deriv, lower_low, higher_high, bull_bear_th

"""
Exponential Moving Average (EMA) - 9 points
Simple Moving Average (SMA)

Stochs w/ SMA(3) --> SMA(3) of the stochs trend
MACD w/ EMA(9) --> EMA(9) of the MACD trend

Signals (Stoch):
If Stoch > 80 / < 20:
    If divergence w/ SMA(3):
        Potential change
    divergence => SMA & stoch cross

Signals (UltimateStoch):
If UStoch > 70 / < 30:
    If divergence w/ share price:
        Potential change


Ultimate stoch: [(4 * Avg7 ) + (2 * Avg14) + (1 * Avg28)] / 7
    Avg(x) = BP(x) / TR(x)
        BP(x) = sum(close - floor[period low OR prior close]) for x days
        TR(x) = sum()
"""



FileToImport = "VTSAX.csv"
key = 'Close'

stats = pd.read_csv(FileToImport)

LOW_TH = 30.0
HIGH_TH = 70.0
BULL_BEAR = 50.0

U_RANGES = [7, 14, 28]

bp = []
tr = []
ushort = []
umed = []
ulong = []

smom = []
mmom = []
lmom = []

ult_osc = []

# Generate the ultimate oscillator values
for i in range(len(stats[key])):
    
    # Handle edge cases first
    if i < 1:
        bp.append(0.0)
        tr.append(0.0)
        low = 0
        high = 0
    else:
        low = np.min([stats['Low'][i], stats['Close'][i-1]])
        high = np.max([stats['High'][i], stats['Close'][i-1]])
        bp.append(np.round(stats['Close'][i] - low, 6))
        tr.append(np.round(high - low, 6))

    if i < U_RANGES[0]:
        ushort.append(0.0)
        smom.append(0.0)
    else:
        shbp = 0.0
        shtr = 0.0
        for j in range(U_RANGES[0]):
            shbp += bp[len(bp)-1-j]
            shtr += tr[len(tr)-1-j]
        ushort.append(np.round(shbp / shtr, 6))
        t = [stats['Close'][i-U_RANGES[0]], stats['Close'][i]]
        smom.append(linear_regression(range(1, 3), t)[0])

    if i < U_RANGES[1]:
        umed.append(0.0)
        mmom.append(0.0)
    else:
        shbp = 0.0
        shtr = 0.0
        for j in range(U_RANGES[1]):
            shbp += bp[len(bp)-1-j]
            shtr += tr[len(tr)-1-j]
        umed.append(np.round(shbp / shtr, 6))
        t = [stats['Close'][i-U_RANGES[1]], stats['Close'][i]]
        mmom.append(linear_regression(range(1, 3), t)[0])

    if i < U_RANGES[2]:
        ulong.append(0.0)
        ult_osc.append(50.0)
        lmom.append(0.0)
    else:
        shbp = 0.0
        shtr = 0.0
        for j in range(U_RANGES[2]):
            shbp += bp[len(bp)-1-j]
            shtr += tr[len(tr)-1-j]
        ulong.append(np.round(shbp / shtr, 6))
        ult_osc.append(np.round(100.0 * ((4.0 * ushort[i]) + (2.0 * umed[i]) + ulong[i]) / 7.0, 6))
        t = [stats['Close'][i-U_RANGES[2]], stats['Close'][i]]
        lmom.append(linear_regression(range(1, 3), t)[0])
    

#dual_plotting(smom, stats['Close'], 'short trend', 'price', 'trading days')
#dual_plotting(mmom, stats['Close'], 'interim trend', 'price', 'trading days')
#dual_plotting(lmom, stats['Close'], 'long trend', 'price', 'trading days')

resist = list(stats['High'][len(stats['High'])-28:len(stats['High'])])
#print(resistance(resist))
supporter = list(stats['Low'][len(stats['Low'])-28:len(stats['Low'])])
#print(support(supporter))

ult_mom = []
for i in range(len(smom)):
    ult_mom.append(((4.0 * lmom[i]) + (2.0 * mmom[i]) + (1.0 * smom[i])) / 7.0)
#dual_plotting(ult_mom, stats['Close'], 'enhanced trend', 'price')

#dual_plotting(ult_mom, ult_osc, 'trend', 'oscillator')

# Generate momentum and rate-of-change calculations
sroc = []
mroc = []
lroc = []
for i in range(len(stats['Close'])):

    if i < U_RANGES[2]:
        sroc.append(1.0)
        mroc.append(1.0)
        lroc.append(1.0)
    else:
        sroc.append(np.round(stats['Close'][i] / stats['Close'][i-U_RANGES[0]], 6))
        mroc.append(np.round(stats['Close'][i] / stats['Close'][i-U_RANGES[1]], 6))
        lroc.append(np.round(stats['Close'][i] / stats['Close'][i-U_RANGES[2]], 6))

local1 = local_minima(stats['Close'])
local1a = pd.DataFrame(local1, columns=['ind', 'val'])
#print(local_minima(local1a['val']))


uMin = 100.0
trigger = []
marker_val = 0.0
marker_ind = 0
for i in range(len(stats['Close'])):

    # Find bullish signal
    if ult_osc[i] < LOW_TH:
        ult1 = ult_osc[i]
        marker_val = stats['Close'][i]
        marker_ind = i 
        lows = lower_low(stats['Close'], marker_val, marker_ind)
        if len(lows) != 0:
            ult2 = ult_osc[lows[len(lows)-1][1]]
        
            if ult2 > ult1:
                start_ind = lows[len(lows)-1][1]
                interval = np.max(ult_osc[i:start_ind+1])
                start_ind = bull_bear_th(ult_osc, start_ind, interval, bull_bear='bull')
                if start_ind is not None:
                    trigger.append(["BULLISH", stats['Date'][start_ind], stats['Close'][start_ind], start_ind])
                    #print("BULLISH - " + str(stats['Date'][start_ind]) + " - " + str(stats['Close'][start_ind]) + " - " + str(start_ind))
    
    # Find bearish signal
    if ult_osc[i] > HIGH_TH:
        ult1 = ult_osc[i]
        marker_val = stats['Close'][i]
        marker_ind = i
        highs = higher_high(stats['Close'], marker_val, marker_ind)
        if len(highs) != 0:
            ult2 = ult_osc[highs[len(highs)-1][1]]

            if ult2 < ult1:
                start_ind = highs[len(highs)-1][1]
                interval = np.min(ult_osc[i:start_ind+1])
                start_ind = bull_bear_th(ult_osc, start_ind, interval, bull_bear='bear')
                if start_ind is not None:
                    trigger.append(["BEARISH", stats['Date'][start_ind], stats['Close'][start_ind], start_ind])
                    #print("BEARISH - " + str(stats['Date'][start_ind]) + " - " + str(stats['Close'][start_ind]) + " - " + str(start_ind))

simplified = []
plots = []
for i in range(len(stats['Close'])):
    plots.append(50.0)
present = False
for i in range(len(trigger)):
    for j in range(len(simplified)):
        if simplified[j][3] == trigger[i][3]:
            present = True
    if not present:
        simplified.append(trigger[i])
        if trigger[i][0] == "BEARISH":
            plots[trigger[i][3]] = 100.0
        else:
            plots[trigger[i][3]] = 0.0
    present = False 

print(simplified)

dual_plotting(stats['Close'], ult_osc, 'price', 'ultimate oscillator', 'trading days')
dual_plotting(stats['Close'], plots, 'price', 'buy-sell signal', 'trading days')

# fig, ax1 = plt.subplots()
# color = 'tab:orange'
# ax1.set_xlabel('trading days')
# ax1.set_ylabel('price', color=color)
# ax1.plot(stats['Close'], color=color)
# ax1.tick_params(axis='y', labelcolor=color)

# ax2 = ax1.twinx()

# color = 'tab:blue'
# ax2.set_ylabel('ultimate oscillator', color=color)
# ax2.plot(ult_osc, color=color)
# ax2.tick_params(axis='y', labelcolor=color)
# ax2.grid()




