import pandas as pd 
import numpy as np 

def find_head_shoulders(extrema: dict) -> dict:
    extrema['features'] = []
    lmax = len(extrema['max'])
    lmin = len(extrema['min'])
    i = 0
    j = 0

    # indexes for potential features
    feature = []

    while (i < lmax) or (j < lmin):        

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