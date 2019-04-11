import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

from libs import full_stochastic

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
"""



FileToImport = "BND.csv"
key = 'Adj Close'

stats = pd.read_csv(FileToImport)

SELL_TH = 80.0
BUY_TH = 20.0

STOCH_K = 14

kk = []
dd = []
stochastic = []

for i in range(STOCH_K-1):
    kk.append(50.0)
    dd.append(50.0)

for i in range(STOCH_K-1, len(stats[key])):
    lows = stats['Low'][i-(STOCH_K-1):i+1]
    highs = stats['High'][i-(STOCH_K-1):i+1]
    low = np.min(lows)
    high = np.max(highs)

    s = [low, high, stats['Close'][i]]

    K = (stats['Close'][i] - low) / (high - low) * 100.0
    kk.append(K)
    
    kLen = len(kk)
    D3 = [kk[kLen-3], kk[kLen-2], kk[kLen-1]]
    D = np.mean(D3)
    dd.append(D)


# for i in range(len(stats[key])):
#     if (kk[i] > SELL_TH) and (dd[i] > SELL_TH):
#         stochastic.append(2)
#     elif (kk[i] < BUY_TH) and (kk[i] < BUY_TH):
#         stochastic.append(0)
#     else:
#         stochastic.append(1)

trend = 0
indicator = 0 # 0 is neutral, 1 is oversold, 2: OS w/ osc > thresh; 3: OB, 4: OB w/ osc <
for i in range(len(stats['Close'])):

    if kk[i] > SELL_TH:
        indicator = 3
        stochastic.append(1)

    elif (indicator == 3) and (kk[i] < SELL_TH):
        indicator = 0
        stochastic.append(2)

    elif kk[i] < BUY_TH:
        indicator = 1
        stochastic.append(1)

    elif (indicator == 1) and (kk[i] > BUY_TH):
        indicator = 0
        stochastic.append(0)

    else:
        stochastic.append(1)
    # if kk[i] > SELL_TH:
    #     if kk[i] < dd[i]:
    #         stochastic.append(2)
    #     else:
    #         stochastic.append(1)
    # elif kk[i] < BUY_TH:
    #     if kk[i] > dd[i]:
    #         stochastic.append(0)
    #     else:
    #         stochastic.append(1)
    # else:
    #     stochastic.append(0)


plt.plot(range(len(kk)), kk, dd)
plt.show()


fig, ax1 = plt.subplots()
color = 'tab:orange'
ax1.set_xlabel('trading days')
ax1.set_ylabel('price', color=color)
ax1.plot(stats[key], color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()

color = 'tab:blue'
ax2.set_ylabel('stoch ratio', color=color)
ax2.plot(stochastic, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.show()

stats = pd.read_csv("NFLX.csv")
print(full_stochastic(stats))