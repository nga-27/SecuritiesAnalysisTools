import pandas as pd
import numpy as np

from datetime import datetime
import json
import os
import pprint

from libs.utils import ProgressBar

SP_500_NAMES = ['^GSPC', 'S&P500', 'SP500', 'GSPC', 'INDEX']
ACCEPTED_ATTS = [
    'statistics',
    'macd',
    'rsi',
    'full_stochastic',
    'ultimate',
    'relative_strength',
    'mci',
    'correlation',
    'futures',
    'moving_average',
    'swing_trade',
    'obv',
    'awesome',
    'momentum_oscillator',
    'bear_bull_power',
    'total_power',
    'swing_trade',
    'hull_moving_average'
]

""" Utilities for creating data metrics for plotting later """


def future_returns(fund: pd.DataFrame, **kwargs):
    """
    Future Returns      Logging data of "futures" time period vs. a past time period

    args:
        fund:           (pd.DataFrame) fund historical data

    optional args:
        futures         (list) list of time windows for future trading days; DEFAULT=[5, 15, 45, 90]
        to_json         (bool) True outputs dates as json-stringifiable; DEFAULT=False
        progress_bar:   (ProgressBar) DEFAULT=None

    returns:
        future:         (dict) future data
    """
    futures = kwargs.get('futures', [5, 15, 45, 90])
    to_json = kwargs.get('to_json', False)
    progress_bar = kwargs.get('progress_bar', None)

    fr_data = {}

    increment = 1.0 / float(len(futures) + 1)
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
        if progress_bar is not None:
            progress_bar.uptick(increment=increment)
    f_data = []
    for i in range(len(fund.index)):
        f_data.append(fund.index[i].strftime("%Y-%m-%d"))
    fr_data['index'] = f_data
    if not to_json:
        df = pd.DataFrame.from_dict(fr_data)
        df.set_index('index', inplace=True)
        return df
    future = {'tabular': fr_data}
    if progress_bar is not None:
        progress_bar.uptick(increment=increment)
    return future


###################################################################

def metadata_to_dataset(config: dict):
    if config.get('exports', {}).get('run'):
        print(f"Exporting datasets...")
        metadata_file = "output/metadata.json"
        if not os.path.exists(metadata_file):
            print(f"WARNING: {metadata_file} does not exist. Exiting...")
            return None

        with open(metadata_file) as json_file:
            m_data = json.load(json_file)
            json_file.close()

            job = metadata_key_filter(config['exports']['fields'], m_data)
            full_data = collate_data(job, m_data)
            groomed_data = groom_data(full_data)
            export_data(groomed_data)

            print(f"Exporting datasets complete.")


def metadata_key_filter(keys: str, metadata: dict) -> dict:
    job_dict = dict()
    key_list = keys.split(' ')
    key_list = [k.strip(' ') for k in key_list]
    key_list = list(filter(lambda x: x != '', key_list))
    key_list = [k.upper() for k in key_list]
    for i, k in enumerate(key_list):
        if k in SP_500_NAMES:
            key_list[i] = "^GSPC"

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
        for att in job['attributes']:
            attr = metadata[ticker].get(att, {}).get('tabular')
            if attr is None:
                attr = metadata['_METRICS_'].get(att, {}).get('tabular')
                if attr is None:
                    continue

            # Flatten tree, if necessary
            if type(attr) == dict:
                keys = attr.keys()
                for key in keys:
                    if type(attr[key]) == dict:
                        sub_keys = attr[key].keys()
                        for sub in sub_keys:
                            if type(attr[key][sub]) == dict:
                                sub_sub_keys = attr[key].keys()
                                for sub_sub in sub_sub_keys:
                                    if type(attr[key][sub][sub_sub]) == dict:
                                        print(
                                            f"WARNING: depth of dictionary exceeded with attribute {att} -> {attr[key][sub][sub_sub].keys()}")
                                    else:
                                        new_name = [att, str(key), str(
                                            sub), str(sub_sub)]
                                        new_name = '-'.join(new_name)
                                        all_data[ticker][new_name] = attr[key][sub][sub_sub]
                            else:
                                new_name = [att, str(key), str(sub)]
                                new_name = '-'.join(new_name)
                                all_data[ticker][new_name] = attr[key][sub]
                    else:
                        new_name = [att, str(key)]
                        new_name = '-'.join(new_name)
                        all_data[ticker][new_name] = attr[key]
            else:
                all_data[ticker][att] = attr

        for att in job['attributes']:
            attr = metadata[ticker].get(att, {}).get('metrics')
            if attr is None:
                attr = metadata['_METRICS_'].get(att, {}).get('metrics')
                if attr is None:
                    continue

            # Flatten tree, if necessary
            if type(attr) == dict:
                keys = attr.keys()
                for key in keys:
                    if type(attr[key]) == dict:
                        sub_keys = attr[key].keys()
                        for sub in sub_keys:
                            if type(attr[key][sub]) == dict:
                                sub_sub_keys = attr[key].keys()
                                for sub_sub in sub_sub_keys:
                                    if type(attr[key][sub][sub_sub]) == dict:
                                        print(
                                            f"WARNING: depth of dictionary exceeded with attribute {att} -> {attr[key][sub][sub_sub].keys()}")
                                    else:
                                        new_name = [att, str(key), str(
                                            sub), str(sub_sub)]
                                        new_name = '-'.join(new_name)
                                        new_name += '-METRICS'
                                        all_data[ticker][new_name] = attr[key][sub][sub_sub]
                            else:
                                new_name = [att, str(key), str(sub)]
                                new_name = '-'.join(new_name)
                                new_name += '-METRICS'
                                all_data[ticker][new_name] = attr[key][sub]
                    else:
                        new_name = [att, str(key)]
                        new_name = '-'.join(new_name)
                        new_name += '-METRICS'
                        all_data[ticker][new_name] = attr[key]
            else:
                new_name = f'{att}-METRICS'
                all_data[ticker][new_name] = attr

    return all_data


def groom_data(data: dict) -> dict:
    min_length = 100000
    new_data = dict()
    for fund in data.keys():
        for key in data[fund].keys():
            if len(data[fund][key]) < min_length:
                min_length = len(data[fund][key])

    for fund in data.keys():
        new_data[fund] = dict()
        for key in data[fund].keys():
            len_old = len(data[fund][key])
            new_data[fund][key] = data[fund][key][len_old - min_length: len_old]

    return new_data


def export_data(all_data: dict):
    exports = dict()
    for fund in all_data.keys():
        index = all_data[fund].get('futures-index', [])
        df = pd.DataFrame.from_dict(all_data[fund])
        if len(index) != 0:
            df.set_index('futures-index')
        exports[fund] = df.copy()

    pathname = 'output/'
    if not os.path.exists(pathname):
        os.mkdir(pathname)
    pathname += 'datasets/'
    if not os.path.exists(pathname):
        os.mkdir(pathname)

    for fund in exports.keys():
        filepath = pathname + fund + '.csv'
        exports[fund].to_csv(filepath)
