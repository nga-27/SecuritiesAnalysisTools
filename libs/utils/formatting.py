import pandas as pd 
import numpy as np 
from datetime import datetime
import os 
import shutil
import glob

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


def configure_temp_dir():
    """ for outputting, as well as temp files """
    if not os.path.exists('output/temp/'):
        if not os.path.exists('output/'):
            os.mkdir('output/')
        os.mkdir('output/temp/')


def remove_temp_dir():
    if os.path.exists('output/temp/'):
        shutil.rmtree('output/temp/')


def create_sub_temp_dir(name):
    if not os.path.exists('output/temp/' + name + '/'):
        os.mkdir('output/temp/' + name + '/')

