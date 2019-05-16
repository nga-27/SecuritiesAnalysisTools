import pandas as pd 
import numpy as np 
from datetime import datetime
import os 
import glob

def name_parser(name: str) -> str:
    """ parses file name to generate fund name """
    name = name.split('.')[0]
    name = name.split('/')
    name = name[len(name)-1]
    return name 


def dir_lister(sp_index: str='^GSPC.csv', directory: str='securities/'):
    file_ext = '*.csv'
    directory = directory + file_ext
    items = glob.glob(directory)
    index_file = None

    for item in items:
        if sp_index in item:
            index_file = item
    if index_file is not None:
        items.remove(index_file)

    return index_file, items
    

def index_extractor(tickers) -> str:
    """ tickers is a str of tickers, separated by a space """
    potential_indexes = ['SPY', '^GSPC']

    for key in potential_indexes:
        if key in tickers:
            return key 

    return None 


def fund_list_extractor(ticker_df: pd.DataFrame) -> list:
    """ Extracts fund names from ticker_df for accessing later """
    funds = []
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
