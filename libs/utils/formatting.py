import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os 
import shutil
import glob
import time
import json 

import yfinance as yf 

def name_parser(name: str) -> str:
    """ parses file name to generate fund name """
    name = name.split('.')[0]
    name = name.split('/')
    name = name[len(name)-1]
    return name 
    

def index_extractor(tickers) -> str:
    """ tickers is a str of tickers, separated by a space """
    potential_indexes = ['^GSPC']
    ind = None

    for key in potential_indexes:
        if key in tickers:
            ind = key 

    return ind 


def index_appender(tickers: str) -> str:
    """ appends ^GSPC to ticker string """
    tickers = tickers + ' ' + '^GSPC'
    return tickers


def fund_list_extractor(ticker_df: pd.DataFrame, config: dict) -> list:
    """ Extracts fund names from ticker_df for accessing later """
    funds = []
    # First check if a single fund (single dimension)
    if 'Open' in ticker_df.keys():
        funds = [config['tickers']]
        return funds

    for key in ticker_df.keys():
        """ Multi-level df, so we need to extract only name key (remove duplicates) """
        if (len(key) > 1) and (key[0] not in funds):
            funds.append(key[0])
    return funds


def dates_extractor_list(df) -> list:
    """ specifically for a fund """
    dates = []
    if type(df) == list:
        for i in range(len(df)):
            dates.append(i)
    else:
        for i in range(len(df.index)):
            date = str(df.index[i])
            date = date.split(' ')[0]
            date = datetime.strptime(date, '%Y-%m-%d')
            dates.append(date)

    return dates


def date_extractor(date, _format=None):
    date = str(date)
    date1 = date.split(' ')[0]
    date2 = datetime.strptime(date1, '%Y-%m-%d')
    if _format == 'str':
        dateX = date1
    elif _format == 'iso':
        dateX = date2.isoformat()
    else:
        dateX = date2 
    return dateX


def get_daterange(period: str='1y') -> list:
    # Note: deprecated for more robust fix of mutual fund responses
    """
    fulltime = datetime.now().strftime('%H:%M:%S')
    # Note, timing can be input to function if desired; central time
    endtime = datetime.strptime('19:00:00', '%H:%M:%S').strftime('%H:%M:%S')
    day_of_week = datetime.today().weekday()

    if (day_of_week < 5):
        # 0: monday, 6: sunday
        if fulltime <= endtime:
            # For mutual funds, take prior day range.
            date = datetime.today()
            y, m, d = period_parser(period)
            new_end = date - timedelta(days=1)
            new_start = new_end - relativedelta(years=y, months=m, days=d)
            end = datetime.strftime(new_end, '%Y-%m-%d')
            start = datetime.strftime(new_start, '%Y-%m-%d')
            return [start, end]
    """
    return [None, None]


def period_parser(period: str):
    """ returns [years, months, days] """
    if 'y' in period:
        yr = period.split('y')[0]
        yr = int(yr)
        return yr, 0, 0
        # Year
    elif 'm' in period:
        m = period.split('m')[0]
        m = int(m)
        return 0, m, 0
        # Month
    elif 'd' in period:
        d = period.split('d')[0]
        d = int(d)
        return 0, 0, d
        # Day
    else:
        return 1, 0, 0

