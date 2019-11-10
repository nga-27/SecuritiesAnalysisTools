import pandas as pd 
import numpy as np 

from datetime import datetime
import json
import os

SP_500_NAMES = ['^GSPC', 'S&P500', 'SP500', 'GSPC', 'INDEX']

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
    metadata_file = "output/metadata.json"
    if not os.path.exists(metadata_file):
        print(f"WARNING: {metadata_file} does not exist. Exiting...")
        return None

    with open(metadata_file) as json_file:
        m_data = json.load(json_file)
        job = metadata_key_filter(config['exports'], m_data)
    

def metadata_key_filter(keys: str, metadata: dict) -> dict:
    job_dict = dict()
    key_list = keys.split(' ')
    key_list = [k.strip(' ') for k in key_list]
    key_list = list(filter(lambda x: x != '', key_list))
    key_list = [k.upper() for k in key_list]
    for i, k in enumerate(key_list):
        if k in SP_500_NAMES:
            key_list[i] = "^GSPC" 

    print(f"metadata keys: {metadata.keys()}")
    print(f"other keys: {key_list}")

    job_dict['attributes'] = []
    job_dict['tickers'] = []

    # for key in key_list:


    return job_dict