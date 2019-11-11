import pandas as pd 
import numpy as np 
import math
import yfinance as yf 

from .formatting import get_daterange, fund_list_extractor


def download_data_indexes(indexes: list, tickers: str, period: str='2y', interval='1d', start=None, end=None) -> list:
    if (start is not None) and (end is not None):
        data1 = yf.download(tickers=tickers, start=start, end=end, interval='1d', group_by='ticker')
    else:
        data1 = yf.download(tickers=tickers, period=period, interval='1d', group_by='ticker')
    data = data_format(data1, config=None, list_of_funds=indexes)
    return data, indexes


def download_data(config: dict) -> list:
    period = config['period']
    interval = config['interval']
    tickers = config['tickers']
    ticker_print = config['ticker print']

    if period is None:
        period = '2y'
    if interval is None:
        interval = '1d'
    
    daterange = get_daterange(period=period)
    
    if daterange[0] is None:
        print(f'Fetching data for {ticker_print} for {period} at {interval} intervals...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker')
    else: 
        print(f'Fetching data for {ticker_print} from dates {daterange[0]} to {daterange[1]}...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker', start=daterange[0], end=daterange[1])
    print(" ")

    funds = fund_list_extractor(data, config=config)
    data = data_format(data, config=config)

    return data, funds



def add_status_message(status: list, new_message: str) -> str:
    """ adds 'new_message' to status if it isn't added already """
    need_to_add = True
    for i, message in enumerate(status):
        if new_message == message['message']:
            status[i]['count'] += 1
            need_to_add = False
    if need_to_add:
        status.append({'message': new_message, 'count': 1})
    return status


def get_status_message(status: list) -> str:
    message = ''
    for i,item in enumerate(status):
        message += f"{item['message']} ({item['count']})"
        if i < len(status)-1:
            message += ', '
    return message



def data_format(data: pd.DataFrame, config: dict, list_of_funds=None) -> dict:
    data_dict = {}
    fund_keys = list_of_funds
    if list_of_funds is None:
        fund_keys = fund_list_extractor(data, config=config)
    dates = data.index 

    if 'Open' in data.keys():
        # Singular fund case
        df_dict = {}
        df_dict['Date'] = dates.copy() 
        df_dict['Open'] = filter_nan(data['Open'].copy(), fund_name=fund_keys[0])
        df_dict['Close'] = filter_nan(data['Close'].copy())
        df_dict['High'] = filter_nan(data['High'].copy())
        df_dict['Low'] = filter_nan(data['Low'].copy())
        df_dict['Adj Close'] = filter_nan(data['Adj Close'].copy())
        df_dict['Volume'] = filter_nan(data['Volume'].copy())

        df = pd.DataFrame.from_dict(df_dict)
        df = df.set_index('Date')

        data_dict[fund_keys[0]] = df.copy()

    else:
        for fund in fund_keys:
            df_dict = {}
            df_dict['Date'] = dates.copy() 
            df_dict['Open'] = filter_nan(data[fund]['Open'].copy(), fund_name=fund)
            df_dict['Close'] = filter_nan(data[fund]['Close'].copy())
            df_dict['High'] = filter_nan(data[fund]['High'].copy())
            df_dict['Low'] = filter_nan(data[fund]['Low'].copy())
            df_dict['Adj Close'] = filter_nan(data[fund]['Adj Close'].copy())
            df_dict['Volume'] = filter_nan(data[fund]['Volume'].copy())

            df = pd.DataFrame.from_dict(df_dict)
            df = df.set_index('Date')

            data_dict[fund] = df.copy()

    return data_dict


def filter_nan(frame_list: pd.DataFrame, fund_name=None) -> list:
    new_list = list(frame_list.copy())
    nans = list(np.where(pd.isna(frame_list) == True))[0]

    corrected = False
    status = []

    if len(nans) > 0:
        corrected = True
        for na in nans:
            if (na == 0) and (not math.isnan(new_list[na+1])):
                status = add_status_message(status, 'Row-0 nan')
                new_list[na] = new_list[na+1]
            elif (na != 0) and (na != len(new_list)-1) and (not math.isnan(new_list[na-1]) and (not math.isnan(new_list[na+1]))):
                status = add_status_message(status, 'Row-inner nan')
                new_list[na] = np.round(np.mean([new_list[na-1], new_list[na+1]]), 2)
            elif (na == len(new_list)-1) and (not math.isnan(new_list[na-1])):
                status = add_status_message(status, 'Mutual Fund nan')
                new_list[na] = new_list[na-1]
            else:
                status = add_status_message(status, 'Unknown/unfixable nan')

    if corrected and (fund_name is not None):
        message = get_status_message(status)
        if 'Unknown/unfixable nan' in message:
            print(f"WARNING: 'NaN' found on {fund_name}. Type: '{message}': Correction FAILED.")
        else:
            print(f"Note: 'NaN' found on {fund_name} data. Type: '{message}': Corrected OK.")
        
    return new_list
