import os
import shutil
import glob
import time
import json
from datetime import datetime, timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta


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


def fund_list_extractor(ticker_df: dict, config: dict = None) -> list:
    """ Extracts fund names from ticker_df for accessing later """
    funds = []
    if config is not None:
        # First check if a single fund (single dimension), only on 0.1.13+
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


def dates_convert_from_index(df: pd.DataFrame, list_of_xlists: list, to_str=False) -> list:
    new_l_of_xls = []
    if len(list_of_xlists) > 0:
        for xlist in list_of_xlists:
            new_xlist = []
            for x in xlist:
                if to_str:
                    date = df.index[x].strftime("%Y-%m-%d")
                else:
                    date = df.index[x]
                new_xlist.append(date)
            new_l_of_xls.append(new_xlist)
    return new_l_of_xls
