import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os 
import shutil
import glob
import time
import json 

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


def get_daterange(period: str='1y'):
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

    return None


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


def windows_compatible_file_parse(extension: str, parser: str='/', desired_len=4, bad_parse='\\') -> list:
    globbed = extension.split('/')
    if len(globbed) < desired_len:
        end = globbed[desired_len-2].split(bad_parse)
        globbed.pop(desired_len-2)
        globbed.append(end[0])
        globbed.append(end[1])
    return globbed



def start_header(update_release: str='2019-06-04', version: str='0.1.01', default='VTI') -> str:
    print(" ")
    print("----------------------------------")
    print("-   Securities Analysis Tools    -")
    print("-                                -")
    print("-             nga-27             -")
    print("-                                -")
    print(f"-       version: {version}          -")
    print(f"-       updated: {update_release}      -")
    print("----------------------------------")
    print(" ")
    time.sleep(1)

    # Default (hitting enter)
    tickers = default

    x = input("Enter stock/fund ticker symbols (e.g. 'VTI VWINX'): ")

    period = None
    interval = None

    if x != '':
        core = header_core_parse(x)
        if core is not None:
            tickers = core[0]
            period = core[1]
            interval = core[2]

        else:
            tickers = x
            if "'" in x:
                spl = x.split("'")
                tickers = spl[1]        
    
    ticker_print = ''
    t = tickers.split(' ')
    if len(t) < 2:
        ticker_print += t[0] + ' and ^GSPC'
    else:
        for i in range(len(t)):
            if t[i] != '':
                ticker_print += t[i] + ', '
        ticker_print += 'and ^GSPC'
    print(" ")
    return tickers, ticker_print, period, interval 


def header_core_parse(input_str: str) -> list:
    if input_str != '--core':
        return None

    if os.path.exists('core.json'):
        tickers = ''
        with open('core.json') as json_file:
            core = json.load(json_file)
            for i in range(len(core['Ticker Symbols'])-1):
                tickers += core['Ticker Symbols'][i] + ' '
            tickers += core['Ticker Symbols'][len(core['Ticker Symbols'])-1]
            interval = core['Properties']['Interval']
            period = core['Properties']['Period']

    return [tickers, period, interval]
