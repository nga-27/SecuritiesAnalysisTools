import pandas as pd 
import numpy as np 

from datetime import datetime

""" Utilities for creating data metrics for plotting later """

def future_returns(fund: pd.DataFrame, futures: list=[5, 15, 45, 90], to_json=False):
    fr_data = {}
    for future in futures:
        f_data = []
        for i in range(len(fund['Close'])-future):
            cur = fund['Close'][i]
            fut = fund['Close'][i+future]
            val = np.round((fut - cur) / cur * 100.0, 3)
            f_data.append(val)
        for i in range(future):
            f_data.append(0.0)
        fr_data[str(future)] = f_data.copy()
    f_data = []
    for i in range(len(fund.index)):
        f_data.append(fund.index[i].strftime("%Y-%m-%d"))
    fr_data['index'] = f_data
    if not to_json:
        df = pd.DataFrame.from_dict(fr_data)
        df.set_index('index', inplace=True)
        return df 
    return fr_data


def metadata_to_dataset(config: dict):
    print(f"metadata_to_dataset: {config['exports']}")