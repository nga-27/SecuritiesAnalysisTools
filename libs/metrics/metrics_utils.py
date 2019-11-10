import pandas as pd 
import numpy as np 

from datetime import datetime
import json
import os
import pprint

SP_500_NAMES = ['^GSPC', 'S&P500', 'SP500', 'GSPC', 'INDEX']
ACCEPTED_ATTS = ['statistics', 
    'macd', 
    'rsi', 
    'relative_strength', 
    'mci', 
    'correlation',
    'futures'
]

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
    future = {'tabular': fr_data}
    return future


###################################################################

def metadata_to_dataset(config: dict):
    print(f"metadata_to_dataset: {config['exports']}")
    metadata_file = "output/metadata.json"
    if not os.path.exists(metadata_file):
        print(f"WARNING: {metadata_file} does not exist. Exiting...")
        return None

    with open(metadata_file) as json_file:
        m_data = json.load(json_file)
        job = metadata_key_filter(config['exports'], m_data)
        pprint.pprint(job)

        full_data = collate_data(job, m_data)


    

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

    for key in key_list:
        if key in metadata.keys():
            job_dict['tickers'].append(key)
    if len(job_dict['tickers']) == 0:
        # "All available tickers" case
        for key in metadata.keys():
            if key != '_METRICS_':
                job_dict['tickers'].append(key)

    temp_key = job_dict['tickers'][0]
    for key in key_list:
        if (key.lower() in metadata[temp_key].keys()) and (key.lower() in ACCEPTED_ATTS):
            job_dict['attributes'].append(key)
        if key.lower() in metadata.get('_METRICS_', {}).keys():
            job_dict['attributes'].append(key)

    if len(job_dict['attributes']) == 0:
        # "All available/accepted attributes" case
        for key in metadata[temp_key].keys():
            if key in ACCEPTED_ATTS:
                job_dict['attributes'].append(key)
        for key in metadata.get('_METRICS_', {}).keys():
            if key in ACCEPTED_ATTS:
                job_dict['attributes'].append(key)

    return job_dict


def collate_data(job: dict, metadata: dict):
    all_data = dict()
    for ticker in job['tickers']:
        all_data[ticker] = dict()
        # print(metadata[ticker].keys())
        for att in job['attributes']:
            print(f"Attribute: {att}")
            attr = metadata[ticker].get(att)
            if type(attr) == dict:
                print(f"att keys: {attr.keys()}")
            elif type(attr) == list:
                print(f"length of list: {len(attr)}")
            else:
                attr = metadata['_METRICS_'].get(att)
                if type(attr) == dict:
                    print(f"att keys: {attr.keys()}")
                elif type(attr) == list:
                    print(f"length of list: {len(attr)}")



    return all_data