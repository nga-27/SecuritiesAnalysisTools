import pandas as pd 
import numpy as np 

from libs.tools import export_macd_nasit_signal
from libs.tools import export_cluster_nasit_signal
from libs.tools import windowed_ma_list
from libs.utils import nasit_cluster_signal, nasit_oscillator_signal
from libs.utils import dual_plotting

def nasit_composite_index(fund: pd.DataFrame) -> list:
    composite = []

    # Pull in nasit signals from indicators
    macd_nasit = export_macd_nasit_signal(fund)
    cluster_nasit = export_cluster_nasit_signal(fund, function='all')

    # Normalize all nasit signals to their max(abs(x))
    macd_max = np.max(np.abs(macd_nasit))
    macd_nasit = [x / macd_max for x in macd_nasit]
    cluster_max = np.max(np.abs(cluster_nasit))
    cluster_nasit = [x / cluster_max for x in cluster_nasit]

    #print(f'cluster: {np.max(cluster_nasit)}, {np.min(cluster_nasit)}')
    #print(f'macd: {np.max(macd_nasit)}, {np.min(macd_nasit)}')

    # Determine weights for each signal, apply
    macd_weight = 0.35
    cluster_weight = 0.65
    macd_n2 = [x * macd_weight for x in macd_nasit]
    cluster_n2 = [x * cluster_weight for x in cluster_nasit]

    # Combine weighted signals
    for i in range(len(cluster_n2)):
        t = cluster_n2[i] + macd_n2[i]
        composite.append(t)
        if i == 150:
            print(f'cluster {cluster_n2[i]}, macd {macd_n2[i]}, total {t}')

    composite = windowed_ma_list(composite, interval=3)

    dual_plotting(fund['Close'], composite, 'Price', 'NASIT', 'Trading Days', title='NASIT COMPOSITE INDEX')

    return composite 
