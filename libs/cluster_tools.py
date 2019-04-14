import pandas as pd 
import numpy as np 

def clustering(updatable: list, evaluator: dict) -> list:
    for bull in evaluator['bullish']:
        index = bull[2]
        updatable[index] += -8 if updatable[index] != 0 else -1
        if index < len(updatable)-1:
            updatable[index-1] += -5 if updatable[index-1] != 0 else 0
            updatable[index+1] += -5 if updatable[index+1] != 0 else 0
        if index < len(updatable)-2:
            updatable[index-2] += -3 if updatable[index-2] != 0 else 0
            updatable[index+2] += -3 if updatable[index+2] != 0 else 0
        if index < len(updatable)-3:
            updatable[index-3] += -2 if updatable[index-3] != 0 else 0
            updatable[index+3] += -2 if updatable[index+3] != 0 else 0

    for bear in evaluator['bearish']:
        index = bear[2]
        updatable[index] += 8 if updatable[index] != 0 else 1
        if index < len(updatable)-1:
            updatable[index-1] += 5 if updatable[index-1] != 0 else 0
            updatable[index+1] += 5 if updatable[index+1] != 0 else 0
        if index < len(updatable)-2:
            updatable[index-2] += 3 if updatable[index-2] != 0 else 0
            updatable[index+2] += 3 if updatable[index+2] != 0 else 0
        if index < len(updatable)-3:
            updatable[index-3] += 2 if updatable[index-3] != 0 else 0
            updatable[index+3] += 2 if updatable[index+3] != 0 else 0

    return updatable



def cluster_filtering(cluster_list: list, filter_thresh: int=7) -> list:
    """ Filters a clustered projection such that any x for (-filter_thresh < f[x] < filter_thresh) = 0 """
    for i in range(len(cluster_list)):
        if (cluster_list[i] < filter_thresh) and (cluster_list[i] > -filter_thresh):
            cluster_list[i] = 0

    return cluster_list