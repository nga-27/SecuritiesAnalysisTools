""" Data Formatting, etc. """
from typing import Tuple, Union
import math

import pandas as pd
import numpy as np
import yfinance as yf

from .formatting import fund_list_extractor
from .constants import STANDARD_COLORS

TICKER = STANDARD_COLORS["ticker"]
NORMAL = STANDARD_COLORS["normal"]
ERROR = STANDARD_COLORS["error"]
NOTE = STANDARD_COLORS["warning"]

"""
period : str
    Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
interval : str
    Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
"""


def download_data_all(config: dict, **kwargs) -> Tuple[dict, list, list, dict]:
    """Download data (for functions)

    Arguments:
        config {dict} -- full information dictionary of entire run

    Optional Args:
        start {str} -- date (default: {None})
        end {str} -- date (default: {None})

    Returns:
        Tuple[dict, list, list, dict] -- downloaded data, list of funds, periods, config
    """
    periods = list(config.get('period', ['2y']))
    interval = config.get('interval', ['1d'])
    tickers = config['tickers']
    ticker_print = config['ticker print']
    start = kwargs.get('start')
    end = kwargs.get('end')

    if len(periods) > len(interval):
        diff = len(periods) - len(interval)
        for _ in range(diff):
            interval.append('1d')
        config['interval'] = interval

    dataset = {}
    funds = []
    for i, per in enumerate(periods):
        inter = interval[i]
        if (start is not None) and (end is not None):
            print(
                f'Fetching data for {TICKER}{ticker_print}{NORMAL} from dates {start} to {end}...')
            data = yf.download(tickers=tickers, period=per, interval=inter,
                               group_by='ticker', start=start, end=end)

        else:
            print(
                f'Fetching data for {TICKER}{ticker_print}{NORMAL} ' +
                f'for {per} at {inter} intervals...')
            data = yf.download(tickers=tickers, period=per, interval=inter, group_by='ticker')

        print(" ")
        funds = fund_list_extractor(data, config=config)
        data = data_format(data, config=config)

        dataset[per] = data
    return dataset, funds, periods, config


def download_data_indexes(indexes: list, tickers: str, **kwargs) -> Tuple[dict, list]:
    """Download Data Indexes

    Arguments:
        indexes {list} -- list of funds
        tickers {str} -- ticker string (e.g. "MMM VTI")

    Optional Args:
        period {str} -- (default: {'2y'})
        interval {str} -- (default: {'1d'})
        start {str} -- date (default: {None})
        end {str} -- date (default: {None})
        fund_len {int} -- (default: {None})

    Returns:
        Tuple[dict, list] -- data of funds, index list
    """
    period = kwargs.get('period', '2y')
    interval = kwargs.get('interval', '1d')
    start = kwargs.get('start')
    end = kwargs.get('end')
    fund_len = kwargs.get('fund_len')

    if (start is not None) and (end is not None):
        data1 = yf.download(tickers=tickers, start=start,
                            end=end, interval=interval, group_by='ticker')

    else:
        data1 = yf.download(tickers=tickers, period=period,
                            interval=interval, group_by='ticker')

    data = data_format(data1, config=None,
                       list_of_funds=indexes, fund_len=fund_len)

    return data, indexes


def download_data(config: dict, **kwargs) -> Tuple[dict, list]:
    """Download data (for functions)

    Arguments:
        config {dict} -- full information dictionary of entire run

    Optional Args:
        start {str} -- date (default: {None})
        end {str} -- date (default: {None})

    Returns:
        Tuple[dict, list] -- downloaded data, list of funds
    """
    period = config.get('period', '2y')
    interval = config.get('interval', '1d')
    tickers = config['tickers']
    ticker_print = config['ticker print']

    start = kwargs.get('start')
    end = kwargs.get('end')
    fund_list_only = kwargs.get('fund_list_only', False)

    if fund_list_only:
        funds = tickers.upper().split(' ')
        return {}, funds

    if isinstance(period, (list)):
        period = period[0]
    if isinstance(interval, (list)):
        interval = interval[0]

    if (start is not None) and (end is not None):
        print(
            f'Fetching data for {TICKER}{ticker_print}{NORMAL} from dates {start} to {end}...')
        data = yf.download(tickers=tickers, period=period, interval=interval,
                           group_by='ticker', start=start, end=end)

    else:
        print(
            f'Fetching data for {TICKER}{ticker_print}{NORMAL} for ' +
            f'{period} at {interval} intervals...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker')

    print(" ")
    funds = fund_list_extractor(data, config=config)
    data = data_format(data, config=config)

    return data, funds


def download_single_fund(fund: str, config: dict, fund_len=None, **kwargs) -> dict:
    """Download Single Fund (api, etc.)

    Arguments:
        fund {str} -- ticker symbol
        config {dict} -- config dict that controls

    Keyword Arguments:
        fund_len {dict} -- start, end to correct datasets (default: {None})

    Optional Arguments:
        start {str} -- date of starting (default: {None})
        end {str} -- date of ending (default: {None})

    Returns:
        dict -- [description]
    """
    period = kwargs.get('period', '2y')
    interval = kwargs.get('interval', '1d')
    ticker = fund
    start = kwargs.get('start')
    end = kwargs.get('end')

    if (start is not None) and (end is not None):
        print("")
        print(
            f'Fetching sector data for {TICKER}{ticker}{NORMAL}...')
        data = yf.download(tickers=ticker, period=period, interval=interval,
                           group_by='ticker', start=start, end=end)

    else:
        print("")
        print(
            f'Fetching sector data for {TICKER}{ticker}{NORMAL}...')
        data = yf.download(tickers=ticker, period=period,
                           interval=interval, group_by='ticker')

    print(" ")

    data = data_format(data, config=config,
                       single_fund_name=ticker, fund_len=fund_len)

    return data


def add_status_message(status: list,
                       new_message: str,
                       message_index: Union[int, None] = None,
                       key: Union[str, None] = None) -> list:
    """Add Status Message

    Adds 'new_message' to status if it isn't added already

    Arguments:
        status {list} -- list of statuses to add to
        new_message {str} -- new message to add to status list

    Keyword Arguments
        message_index {int} -- fund index the status occurred (default: {None})
        key {str} -- a particular key added to 'info' (default: {None})

    Returns:
        list -- status lists
    """
    need_to_add = True
    for i, message in enumerate(status):
        if new_message == message['message']:
            status[i]['count'] += 1
            if key is not None:
                status[i]['info'].append({key: message_index})
            need_to_add = False

    if need_to_add:
        if key is not None:
            status.append({'message': new_message, 'count': 1,
                           'info': [{key: message_index}]})
        else:
            status.append({'message': new_message, 'count': 1, 'info': []})

    return status


def get_status_message(status: list) -> str:
    """Get Status Message

    Arguments:
        status {list} -- status list

    Returns:
        str -- concatenated message and info
    """
    message = ''
    info = ''
    for i, item in enumerate(status):
        message += f"{item['message']} ({item['count']})"
        info += f"{item['info']}"

        if i < len(status)-1:
            message += ', '
            info += ', '

    return message, info


def data_format(data: pd.DataFrame, config: dict, **kwargs) -> dict:
    """Data Format

    Aligns data in a more accessible way (dict of pd.DataFrames)

    Arguments:
        data {pd.DataFrame} -- entire historical data of all funds
        config {dict} -- controlling config structure

    Optional Args:
        list_of_funds {list} -- list of ticker symbols (default: {None})
        single_fund_name {str} -- for single fund cases, is ticker name (default: {None})
        fund_len {dict} -- start, end for error correction (default: {None})

    Returns:
        dict -- reformmated data, error checked
    """
    list_of_funds = kwargs.get('list_of_funds')
    single_fund_name = kwargs.get('single_fund_name')
    fund_len = kwargs.get('fund_len')
    data_dict = {}
    fund_keys = list_of_funds
    if list_of_funds is None:
        if single_fund_name is None:
            fund_keys = fund_list_extractor(data, config=config)
        else:
            fund_keys = [single_fund_name]
    dates = data.index

    if 'Open' in data.keys():
        # Singular fund case
        df_dict = {}
        df_dict['Date'] = filter_date(dates.copy(), fund_len=fund_len)
        df_dict['Open'] = filter_nan(data['Open'].copy(), column_key='Open', fund_len=fund_len)
        df_dict['Close'] = filter_nan(
            data['Close'].copy(), column_key='Close', fund_len=fund_len)
        df_dict['High'] = filter_nan(
            data['High'].copy(), column_key='High', fund_len=fund_len)
        df_dict['Low'] = filter_nan(
            data['Low'].copy(), column_key='Low', fund_len=fund_len)
        df_dict['Adj Close'] = filter_nan(
            data['Adj Close'].copy(), column_key='Adj Close', fund_len=fund_len)
        df_dict['Volume'] = filter_nan(
            data['Volume'].copy(), fund_name=fund_keys[0], column_key='Volume', fund_len=fund_len)

        data_frame = pd.DataFrame.from_dict(df_dict)
        data_frame = data_frame.set_index('Date')
        data_dict[fund_keys[0]] = data_frame.copy()

    else:
        for fund in fund_keys:
            df_dict = {}
            df_dict['Date'] = filter_date(dates.copy(), fund_len=fund_len)
            df_dict['Open'] = filter_nan(data[fund]['Open'].copy(),
                fund_name=fund, column_key='Open', fund_len=fund_len)
            df_dict['Close'] = filter_nan(
                data[fund]['Close'].copy(), column_key='Close', fund_len=fund_len)
            df_dict['High'] = filter_nan(
                data[fund]['High'].copy(), column_key='High', fund_len=fund_len)
            df_dict['Low'] = filter_nan(
                data[fund]['Low'].copy(), column_key='Low', fund_len=fund_len)
            df_dict['Adj Close'] = filter_nan(
                data[fund]['Adj Close'].copy(), column_key='Adj Close', fund_len=fund_len)
            df_dict['Volume'] = filter_nan(
                data[fund]['Volume'].copy(), column_key='Volume', fund_len=fund_len)

            data_frame = pd.DataFrame.from_dict(df_dict)
            data_frame = data_frame.set_index('Date')
            data_dict[fund] = data_frame.copy()

    return data_dict


def filter_nan(frame_list: pd.DataFrame, **kwargs) -> list:
    """Filter NaN

    Removes "not a number" (NaN) values from fund if possible, usually due to a yfinance error.

    Arguments:
        frame_list {pd.DataFrame} -- fund dataset to cleanse, if needed

    Optional Args:
        fund_name {str} -- name of fund (default: {None})
        column_key {str} -- name of column (default: {None})
        fund_len {dict} -- length of desired list (default: {None})

    Returns:
        list -- newly, cleansed dataframe column
    """
    # pylint: disable=too-many-branches,too-many-statements
    fund_name = kwargs.get('fund_name')
    column_key = kwargs.get('column_key')
    fund_len = kwargs.get('fund_len')

    new_list = list(frame_list.copy())
    nans = list(np.where(pd.isna(frame_list)))[0]

    corrected = False
    status = []

    if fund_len is not None:
        if len(new_list) != fund_len['length']:
            if frame_list.index[0] != fund_len['start']:
                newer_list = [float('NaN')]
                newer_list.extend(new_list)
                new_list = newer_list.copy()
                nans = insert_into_sorted_nans(nans, 0)

            elif frame_list.index[len(frame_list)-1] != fund_len['end']:
                new_list.append(float('NaN'))
                nans = insert_into_sorted_nans(nans, len(frame_list)-1)

            else:
                newer_list = []
                f_count = 0
                d_count = 0

                while (d_count < len(fund_len['dates'])) and (f_count < len(frame_list.index)):
                    if fund_len['dates'][d_count] == frame_list.index[f_count]:
                        newer_list.append(frame_list[f_count])
                        f_count += 1
                        d_count += 1

                    elif fund_len['dates'][d_count] < frame_list.index[f_count]:
                        newer_list.append(float('NaN'))
                        nans = insert_into_sorted_nans(nans, d_count)
                        d_count += 1

                    else:
                        newer_list.append(frame_list[f_count])
                        f_count += 1

                new_list = newer_list.copy()

    if len(nans) > 0:
        corrected = True
        for nan_val in nans:
            if (nan_val == 0) and (not math.isnan(new_list[nan_val + 1])):
                status = add_status_message(status, 'Row-0 nan')
                new_list[nan_val] = new_list[nan_val + 1]

            elif (nan_val != 0) and \
                (nan_val != len(new_list)-1) and \
                    (not math.isnan(new_list[nan_val - 1]) and \
                        (not math.isnan(new_list[nan_val + 1]))):
                status = add_status_message(status, 'Row-inner nan')
                new_list[nan_val] = np.round(
                    np.mean([new_list[nan_val - 1], new_list[nan_val + 1]]), 2)

            elif (nan_val == len(new_list)-1) and (not math.isnan(new_list[nan_val - 1])):
                status = add_status_message(status, 'Mutual Fund nan')
                new_list[nan_val] = new_list[nan_val - 1]

            elif not math.isnan(new_list[nan_val - 1]):
                # More general case than above, different error.
                status = add_status_message(
                    status, 'Generic progression nan', nan_val, column_key)
                new_list[nan_val] = new_list[nan_val - 1]

            elif (nan_val < len(new_list)-2) and (not math.isnan(new_list[nan_val + 1])):
                status = add_status_message(
                    status, 'Generic progression nan', nan_val, column_key)
                new_list[nan_val] = new_list[nan_val + 1]

            else:
                status = add_status_message(
                    status, 'Unknown/unfixable nan', nan_val, column_key)

    if corrected and (fund_name is not None):
        message, info = get_status_message(status)
        if 'Unknown/unfixable nan' in message:
            print(
                f"{ERROR}WARNING: 'NaN' found on {fund_name}. Type: '{message}': " +
                "Correction FAILED.")
            print(f"----> Content: {info}{NORMAL}")

        elif 'Generic progression nan' in message:
            print(
                f"{NOTE}Note: 'NaN' found on {fund_name}. Type: '{message}': Corrected OK.")
            print(f"----> Content: {info}{NORMAL}")

        else:
            print(
                f"{NOTE}Note: 'NaN' found on {fund_name} data. Type: '{message}': " +
                f"Corrected OK.{NORMAL}")

    return new_list


def filter_date(dates, fund_len: dict = None) -> list:
    """Filter Date

    Arguments:
        dates {list, pd.DataFrame} -- dates of a dataframe or list

    Keyword Arguments:
        fund_len {dict} -- desired length of date (default: {None})

    Returns:
        list -- list of cleansed dates
    """
    if fund_len is not None:
        if len(dates) != fund_len['length']:
            if dates[0] != fund_len['start']:
                newer_list = [fund_len['start']]
                newer_list.extend(dates)
                dates = newer_list.copy()

            elif dates[len(dates)-1] != fund_len['end']:
                dates.append(fund_len['end'])

            else:
                newer_list = []
                f_count = 0
                d_count = 0

                while (d_count < len(fund_len['dates'])) and (f_count < len(dates)):
                    if fund_len['dates'][d_count] == dates[f_count]:
                        newer_list.append(dates[f_count])
                        f_count += 1
                        d_count += 1

                    elif fund_len['dates'][d_count] < dates[f_count]:
                        newer_list.append(fund_len['dates'][d_count])
                        d_count += 1

                    else:
                        newer_list.append(dates[f_count])
                        f_count += 1

                dates = newer_list.copy()
    return dates.copy()


def insert_into_sorted_nans(nans: list, element: int) -> list:
    """Insert into Sorted NaNs

    Utilized when a missing length of fund is inserted

    Arguments:
        nans {list} -- list of not a numbers
        element {int} -- specific index

    Returns:
        list -- new NaN list
    """
    counter = 0
    new_nans = []
    while (counter < len(nans)) and (nans[counter] < element):
        new_nans.append(nans[counter])
        counter += 1

    new_nans.append(element)
    if counter != len(nans):
        for i in range(counter, len(nans)):
            new_nans.append(nans[i])

    return new_nans
