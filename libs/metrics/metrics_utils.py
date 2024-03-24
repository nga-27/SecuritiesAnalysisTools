""" metrics utils """
import json
import os
from typing import Union, Dict, Tuple, List

import pandas as pd
import numpy as np

from libs.utils import INDICATOR_NAMES
from libs.utils.progress_bar import ProgressBar, update_progress_bar
from libs.utils.formatting import append_index
from libs.utils import STANDARD_COLORS

WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]

SP_500_NAMES = ['^GSPC', 'S&P500', 'SP500', 'GSPC', 'INDEX']

# Utilities for creating data metrics for plotting later


def future_returns(fund: pd.DataFrame, **kwargs) -> Union[pd.DataFrame, dict]:
    """Future Returns

    Logging data of "futures" time period vs. a past time period

    Arguments:
        fund {pd.DataFrame} -- fund historical data

    Optional Args:
        futures {list} -- list of time windows for future trading days (default: {5, 15, 45, 90})
        to_json {bool} -- True outputs dates as json-stringifiable (default: {True})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- future data
    """
    futures = kwargs.get('futures', [5, 15, 45, 90])
    to_json = kwargs.get('to_json', True)
    progress_bar: Union[ProgressBar, None] = kwargs.get('progress_bar')

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
        update_progress_bar(progress_bar, increment)

    f_data = []
    for index_value in fund.index:
        f_data.append(index_value.strftime("%Y-%m-%d"))

    fr_data['index'] = f_data
    if not to_json:
        data_frame = pd.DataFrame.from_dict(fr_data)
        data_frame.set_index('index', inplace=True)
        return data_frame

    future = {'tabular': fr_data}
    update_progress_bar(progress_bar, increment)

    future['type'] = 'future'
    return future


def metadata_to_dataset(config: dict):
    """Metadata to Dataset

    Arguments:
        config {dict} -- configuration obj

    """
    if config.get('exports', {}).get('run'):
        print("Exporting datasets...")
        metadata_file = os.path.join("output", "metadata.json")
        if not os.path.exists(metadata_file):
            print(f"WARNING: {metadata_file} does not exist. Exiting...")
            return

        with open(metadata_file, encoding='utf-8') as json_file:
            m_data = json.load(json_file)
            json_file.close()

            job = metadata_key_filter(config['exports']['fields'], m_data)
            full_data = collate_data(job, m_data)
            full_data = collate_data_periods(job, m_data, all_data=full_data)
            groomed_data = groom_data(full_data)
            export_data(groomed_data)
            print("Exporting datasets complete.")


def metadata_key_filter(keys: str, metadata: dict) -> dict:
    """Metadata Key Filter

    Arguments:
        keys {str} -- keys to split
        metadata {dict} -- metadata data object

    Returns:
        dict -- filtered metadata data object
    """
    # pylint: disable=too-many-branches
    job_dict = {}
    key_list = keys.split(' ')
    key_list = [k.strip(' ') for k in key_list]
    key_list = list(filter(lambda x: x != '', key_list))
    key_list = [k.upper() for k in key_list]
    for i, k in enumerate(key_list):
        if k in SP_500_NAMES:
            key_list[i] = "^GSPC"

    job_dict['attributes'] = []
    job_dict['tickers'] = []
    job_dict['periods'] = []

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
        if (key.lower() in metadata[temp_key].keys()) and (key.lower() in INDICATOR_NAMES):
            job_dict['attributes'].append(key)
        if key.lower() in metadata.get('_METRICS_', {}).keys():
            job_dict['attributes'].append(key)

    if len(job_dict['attributes']) == 0:
        # "All available/accepted attributes" case
        for key in metadata[temp_key].keys():
            if 'y' in key:
                job_dict['periods'].append(key)
                for key2 in metadata[temp_key][key]:
                    if key2 in INDICATOR_NAMES:
                        job_dict['attributes'].append(key2)

        for key in metadata.get('_METRICS_', {}).keys():
            if key in INDICATOR_NAMES:
                job_dict['attributes'].append(key)

    return job_dict


def collate_data(job: dict, metadata: dict) -> dict:
    """collate_data

    Args:
        job (dict): tickers and attributes
        metadata (dict): metadata dict

    Returns:
        dict: all data
    """
    # pylint: disable=too-many-branches,too-many-statements,too-many-nested-blocks
    all_data = {}
    for ticker in job['tickers']:
        all_data[ticker] = {}
        for att in job['attributes']:
            attr = metadata[ticker].get(att, {}).get('tabular')
            if attr is None:
                attr = metadata['_METRICS_'].get(att, {}).get('tabular')
                if attr is None:
                    continue

            # Flatten tree, if necessary
            if isinstance(attr, dict):
                keys = attr.keys()
                for key in keys:

                    if isinstance(attr[key], dict):
                        sub_keys = list(attr[key])

                        for sub in sub_keys:
                            if isinstance(attr[key][sub], dict):
                                sub_sub_keys = list(attr[key])

                                for sub_sub in sub_sub_keys:
                                    if isinstance(attr[key][sub][sub_sub], dict):
                                        print(
                                            "WARNING: depth of dictionary exceeded with " +
                                            f"attribute {att} -> {attr[key][sub][sub_sub].keys()}")

                                    else:
                                        new_name = [att, str(key), str(sub), str(sub_sub)]
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
            if isinstance(attr, dict):
                keys = attr.keys()

                for key in keys:
                    if isinstance(attr[key], dict):
                        sub_keys = attr[key].keys()

                        for sub in sub_keys:
                            if isinstance(attr[key][sub], dict):
                                sub_sub_keys = attr[key].keys()

                                for sub_sub in sub_sub_keys:
                                    if isinstance(attr[key][sub][sub_sub], dict):
                                        print(
                                            "WARNING: depth of dictionary exceeded " +
                                                f"with attribute {att} -> " +
                                                f"{attr[key][sub][sub_sub].keys()}")
                                    else:
                                        new_name = [att, str(key), str(sub), str(sub_sub)]
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


def collate_data_periods(job: dict, metadata: dict, all_data: Union[dict, None] = None) -> dict:
    """collate_data_periods

    Args:
        job (dict): job dictionary
        metadata (dict): metadata dictionary
        all_data (dict, optional): data to be collated. Defaults to None.

    Returns:
        dict: all_data
    """
    # pylint: disable=too-many-branches,too-many-statements,too-many-nested-blocks
    if all_data is None:
        all_data = {}

    # pylint: disable=too-many-nested-blocks
    for ticker in job['tickers']:
        all_data[ticker] = {}

        for period in job['periods']:
            for att in job['attributes']:
                attr = metadata[ticker][period].get(att, {}).get('tabular')
                if attr is None:
                    continue

                # Flatten tree, if necessary
                if isinstance(attr, dict):
                    keys = attr.keys()

                    for key in keys:
                        if isinstance(attr[key], dict):
                            sub_keys = attr[key].keys()

                            for sub in sub_keys:
                                if isinstance(attr[key][sub], dict):
                                    sub_sub_keys = attr[key].keys()

                                    for sub_sub in sub_sub_keys:
                                        if isinstance(attr[key][sub][sub_sub], dict):
                                            print(
                                                "WARNING: depth of dictionary exceeded with " +
                                                f"attribute {att} -> " +
                                                f"{attr[key][sub][sub_sub].keys()}")
                                        else:
                                            new_name = [period, att, str(key), str(
                                                sub), str(sub_sub)]
                                            new_name = '-'.join(new_name)
                                            all_data[ticker][new_name] = attr[key][sub][sub_sub]

                                else:
                                    new_name = [period, att, str(key), str(sub)]
                                    new_name = '-'.join(new_name)
                                    all_data[ticker][new_name] = attr[key][sub]

                        else:
                            new_name = [period, att, str(key)]
                            new_name = '-'.join(new_name)
                            all_data[ticker][new_name] = attr[key]

                else:
                    new_name = [period, att]
                    new_name = '_'.join(new_name)
                    all_data[ticker][new_name] = attr

            for att in job['attributes']:
                attr = metadata[ticker][period].get(att, {}).get('metrics')
                if attr is None:
                    continue

                # Flatten tree, if necessary
                if isinstance(attr, dict):
                    keys = attr.keys()

                    for key in keys:
                        if isinstance(attr[key], dict):
                            sub_keys = attr[key].keys()

                            for sub in sub_keys:
                                if isinstance(attr[key][sub], dict):
                                    sub_sub_keys = attr[key].keys()

                                    for sub_sub in sub_sub_keys:
                                        if isinstance(attr[key][sub][sub_sub], dict):
                                            print(
                                                "WARNING: depth of dictionary exceeded with " +
                                                f"attribute {att} -> " +
                                                f"{attr[key][sub][sub_sub].keys()}")
                                        else:
                                            new_name = [period, att, str(key), str(
                                                sub), str(sub_sub)]
                                            new_name = '-'.join(new_name)
                                            new_name += '-METRICS'
                                            all_data[ticker][new_name] = attr[key][sub][sub_sub]

                                else:
                                    new_name = [period, att, str(key), str(sub)]
                                    new_name = '-'.join(new_name)
                                    new_name += '-METRICS'
                                    all_data[ticker][new_name] = attr[key][sub]

                        else:
                            new_name = [period, att, str(key)]
                            new_name = '-'.join(new_name)
                            new_name += '-METRICS'
                            all_data[ticker][new_name] = attr[key]

                else:
                    new_name = f'{period}-{att}-METRICS'
                    all_data[ticker][new_name] = attr

    return all_data


def groom_data(data: dict) -> dict:
    """Groom Data

    Find the longest tabular data column, and extend all other columns to match that
    by adding zeros.

    Arguments:
        data {dict} -- data to groom

    Returns:
        dict -- groomed data
    """
    max_len = 0
    new_data = {}
    for fund in data.keys():
        for key in data[fund].keys():
            max_len = max(max_len, data[fund][key])

    for fund in data.keys():
        new_data[fund] = {}
        for key in data[fund].keys():
            len_old = len(data[fund][key])
            temp = [0.0] * (max_len - len_old)
            temp.extend(data[fund][key])
            new_data[fund][key] = temp

    return new_data


def export_data(all_data: dict):
    """Export Data

    Arguments:
        all_data {dict} -- data object to export
    """
    exports: Dict[str, pd.DataFrame] = {}
    for fund in all_data.keys():
        index = all_data[fund].get('futures-index', [])
        data_frame = pd.DataFrame.from_dict(all_data[fund])
        if len(index) != 0:
            data_frame.set_index('futures-index')
        exports[fund] = data_frame.copy()

    pathname = 'output'
    if not os.path.exists(pathname):
        os.mkdir(pathname)

    pathname = os.path.join("output", "datasets")
    if not os.path.exists(pathname):
        os.mkdir(pathname)

    for fund, value in exports.items():
        filepath = os.path.join(pathname, f"{fund}.csv")
        value.to_csv(filepath)


def get_metrics_file_path() -> Union[str, None]:
    """ Returns filepath if valid and present, else None """
    metrics_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(metrics_file):
        print(
            f"{WARNING}WARNING: '{metrics_file}' not found for " +
            f"'metrics_initializer'. Failed.{NORMAL}")
        return None
    return metrics_file


def get_tickers_and_period(ticker_str: str, period: Union[List[str], str]) -> Tuple[List[str], str]:
    """Configure ticker list and period for metrics initializers

    Args:
        ticker_str (str): ticker string on startup
        period (Union[List[str], str]): period as a str or list of periods as strings

    Returns:
        Tuple[List[str], str]: list of tickers, single period
    """
    tickers = append_index(ticker_str)
    all_tickers = tickers.split(' ')
    if isinstance(period, list):
        period = period[0]
    return all_tickers, period


def get_vertical_sum_list(composite: List[List[float]]) -> List[float]:
    """ Generates a vertical sum of list of lists """
    composite2 = []
    for i in range(len(composite[0])):
        s_val = 0.0
        for j_val in composite:
            s_val += float(j_val[i])
        composite2.append(s_val)
    return composite2
