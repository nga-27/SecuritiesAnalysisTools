import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

fund = pd.read_csv('UNH.csv')
FILTER_SIZE = 10

def head_and_shoulders(fund: pd.DataFrame):
    """ Find head and shoulders feature of a reversal """

    ma = exponential_ma(fund, FILTER_SIZE)
    ex = local_extrema(ma)
    r = reconstruct_extrema(fund['Close'], ex, FILTER_SIZE)
    r = duplicates(r)
    hs = find_h_s(r) 
    
    return hs, ma


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


def local_extrema(filtered: list) -> dict:
    extrema = {}
    extrema['max'] = []
    extrema['min'] = []
    direct = 0
    for i in range(1, len(filtered)):
        if direct == 0:
            if filtered[i] > filtered[i-1]:
                direct = 1
            else:
                direct = -1
        elif direct == 1:
            if filtered[i] < filtered[i-1]:
                direct = -1
                extrema['max'].append(i-1)
        else:
            if filtered[i] > filtered[i-1]:
                direct = 1
                extrema['min'].append(i-1)

    return extrema


def plotter(a1, a2=[]):
    plt.plot(a1)
    if len(a2) > 0:
        plt.plot(a2)
    plt.show()


def reconstruct_extrema(original, extrema: dict, ma_size: int) -> dict:
    recon = {}
    recon['max'] = []
    recon['min'] = []
    olist = list(original)

    for _max in extrema['max']:
        start = _max - ma_size
        if start < 0:
            start = 0
        recon['max'].append([olist.index(np.max(olist[start:_max]), start, _max), np.max(olist[start:_max+1])])

    for _min in extrema['min']:
        start = _min - ma_size
        if start < 0:
            start = 0
        recon['min'].append([olist.index(np.min(olist[start:_min]), start, _min), np.min(olist[start:_min+1])])
    
    return recon


def duplicates(recon: dict) -> dict:
    most_recent = 0
    newlist = []
    for i in range(len(recon['max'])):
        if (recon['max'][i][0] != most_recent) and ((recon['max'][i][1] > recon['max'][i-1][1] * 1.01) or (recon['max'][i][1] < recon['max'][i-1][1] * 0.99)):
            most_recent = recon['max'][i][0]
            newlist.append(recon['max'][i])
    recon['max'] = newlist
    newlist = []
    most_recent = 0
    for i in range(len(recon['min'])):
        if (recon['min'][i][0] != most_recent) and ((recon['min'][i][1] > recon['min'][i-1][1] * 1.01) or (recon['min'][i][1] < recon['min'][i-1][1] * 0.99)):
            most_recent = recon['min'][i][0]
            newlist.append(recon['min'][i])
    recon['min'] = newlist

    return recon 



def find_h_s(extrema: dict) -> dict:
    extrema['features'] = []
    lmax = len(extrema['max'])
    lmin = len(extrema['min'])
    i = 0
    j = 0

    # indexes for potential features
    feature = []

    while (i < lmax) or (j < lmin):
        print(feature)
        

        if (i < lmax) and (j < lmin): 
            if extrema['max'][i][0] < extrema['min'][j][0]:
                feature.append([extrema['max'][i][0], extrema['max'][i][1]])
                i += 1
            else:
                feature.append([extrema['min'][j][0], extrema['min'][j][1]])
                j += 1
           
        elif (j < lmin):
            feature.append([extrema['min'][j][0], extrema['min'][j][1]])
            j += 1

        elif (i < lmax):
            feature.append([extrema['max'][i][0], extrema['max'][i][1]])
            i += 1
            
        else:
            break 

        if len(feature) > 5:
            feature.pop(0) 

        if len(feature) == 5:
            extrema['features'].append(feature_detection(feature))

    return extrema


def feature_detection(features: list) -> dict:
    detected = {}
    #print(features)
    if features[0][1] > features[1][1]:
        # potential 'W' case (bearish)
        m1 = features[0][1]
        n1 = features[1][1]
        if (features[2][1] > m1) and (features[2][1] > n1):
            m2 = features[2][1]
            n2 = features[3][1]
            if (features[4][1] < m2) and (features[4][1] > n2):
                # Head and shoulders -> bearish
                detected['type'] = 'bearish'
                detected['neckline'] = {'slope': 0.0, 'intercept': 0.0}
                slope = (n2 - n1) / float(features[3][0] - features[1][0])
                detected['neckline']['slope'] = slope
                intercept = n1 - slope * float(features[1][0])
                detected['neckline']['intercept'] = intercept
                detected['indexes'] = features.copy()
                detected['stats'] = {'width': 0, 'avg': 0.0, 'stdev': 0.0, 'percent': 0.0}
                detected['stats']['width'] = features[4][0] - features[0][0]
                f = features.copy()
                f = [f[i][1] for i in range(len(f))]
                detected['stats']['avg'] = np.round(np.mean(f), 3)
                detected['stats']['stdev'] = np.round(np.std(f), 3)
                detected['stats']['percent'] = np.round(100.0 * np.std(f) / np.mean(f), 3)


    else:
        # potential 'M' case (bullish)
        m1 = features[0][1]
        n1 = features[1][1]
        if (features[2][1] < m1) and (features[2][1] < n1):
            m2 = features[2][1]
            n2 = features[3][1]
            if (features[4][1] > m2) and (features[4][1] < n2):
                # Head and shoulders -> bullish
                detected['type'] = 'bullish'
                detected['neckline'] = {'slope': 0.0, 'intercept': 0.0}
                slope = (n2 - n1) / float(features[3][0] - features[1][0])
                detected['neckline']['slope'] = slope
                intercept = n1 - slope * float(features[1][0])
                detected['neckline']['intercept'] = intercept
                detected['indexes'] = features.copy()
                detected['stats'] = {'width': 0, 'avg': 0.0, 'stdev': 0.0, 'percent': 0.0}
                detected['stats']['width'] = features[4][0] - features[0][0]
                f = features.copy()
                f = [f[i][1] for i in range(len(f))]
                detected['stats']['avg'] = np.round(np.mean(f), 3)
                detected['stats']['stdev'] = np.round(np.std(f), 3)
                detected['stats']['percent'] = np.round(100.0 * np.std(f) / np.mean(f), 3)

    return detected
                




p, ma = head_and_shoulders(fund)
print("")
for feat in p['features']:
    print(feat)
plt.plot(fund['Close'])
plt.plot(ma)
plt.show()