import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os 
import shutil
import glob
import time
import json 

from .constants import TEXT_COLOR_MAP

outline_color = TEXT_COLOR_MAP["blue"]
normal_color = TEXT_COLOR_MAP["white"]
author_color = TEXT_COLOR_MAP["purple"]

def start_header(update_release: str='2019-06-04', version: str='0.1.01', default='VTI', options: str=None) -> dict:
    print(" ")
    print(f"{outline_color}----------------------------------")
    print(f"-{normal_color}   Securities Analysis Tools    {outline_color}-")
    print(f"-                                -")
    print(f"-{author_color}            nga-27              {outline_color}-")
    print(f"-                                -")
    print(f"-{normal_color}       version: {version}          {outline_color}-")
    print(f"-{normal_color}       updated: {update_release}      {outline_color}-")
    print(f"----------------------------------{normal_color}")
    print(" ")

    time.sleep(1)
    config = dict()

    if options is not None:
        input_str = input("Enter ticker symbols (e.g. 'aapl MSFT') and tags (see --options): ")
    else:
        input_str = input("Enter ticker symbols (e.g. 'aapl MSFT'): ")

    config['version'] = version
    config['date_release'] = update_release

    config['state'] = 'run'
    config['period'] = '2y'
    config['interval'] = '1d'
    config['properties'] = {}
    config['core'] = False
    config['tickers'] = ''
    config['exports'] = {"run": False, "fields": []}

    config, list_of_tickers = header_options_parse(input_str, config)
    
    if config['state'] == 'halt':
        return config
    if config['state'] == 'function':
        return config

    if (len(list_of_tickers) == 0) and (config['core'] == False):
        # Default (hitting enter)
        config['tickers'] = default

    else:
        if config['core'] == False:
            config['tickers'] = ticker_list_to_str(list_of_tickers)
            config['tickers'] = config['tickers'].strip()        
    
    config['tickers'] = config['tickers'].upper()
    ticker_print = ''

    # whitespace fixing on input strings
    t, config = remove_whitespace(config, default=default)

    if len(t) < 2:
        if 'no_index' not in config['state']:
            ticker_print += t[0] + ' and S&P500'
        else:
            ticker_print += t[0]
    else:
        ticker_print = ', '.join(t)
        if 'no_index' not in config['state']:
            ticker_print += ', and S&P500'
    config['ticker print'] = ticker_print
    print(" ")
    return config 



def remove_whitespace(config: dict, default: str) -> list:
    # Remove '' entries in list
    t2 = config['tickers'].split(' ')
    t = []
    for t1 in t2:
        if t1 != '':
            t.append(t1)
    if len(t) == 0:
        config['tickers'] = default
        t = config['tickers'].split(' ')
    return t, config


def remove_whitespace_str(input_str: str) -> str:
    s = input_str.split(' ')
    s1 = []
    for s2 in s:
        if s2 != '':
            s1.append(s2)
    if len(s1) == 0:
        return ''
    s = ' '.join(s1)
    return s


def header_json_parse(key: str) -> list:
    json_path = ''
    if key == '--core':
        json_path = 'core.json'
    if key == '--test':
        json_path = 'test.json'

    if os.path.exists(json_path):
        tickers = ''
        with open(json_path) as json_file:
            core = json.load(json_file)
            tickers = ' '.join(core['Ticker Symbols'])
            props = core['Properties']
            interval = props['Interval']
            period = props['Period']
            exports = core.get('Exports')
    
    else:
        return None

    return [tickers, period, interval, props, exports]


def key_parser(input_str: str) -> list:
    keys = input_str.split(' ')
    i_keys = []
    o_keys = []
    for key in keys:
        if key != '':
            o_keys.append(key)
    ticks = []
    for key in o_keys:
        if '--' not in key:
            ticks.append(key)
        else:
            i_keys.append(key)

    return i_keys, ticks


def ticker_list_to_str(ticker_list: list) -> str:
    tick_str = ''
    for tick in ticker_list:
        tick_str += tick + ' '
    return tick_str

####################################################################

def header_options_parse(input_str: str, config: dict) -> list:
    """ Input flag handling """

    config['state'] = ''
    config['run_functions'] = []
    i_keys, ticker_keys = key_parser(input_str)

    if '--options' in i_keys:
        options_file = 'resources/header_options.txt'
        if os.path.exists(options_file):
            fs = open(options_file, 'r')
            options_read = fs.read()
            fs.close()
            print(" ")
            print(options_read)
            print(" ")
        else:
            print(f"ERROR - NO {options_file} found.")
            print(" ")
        config['state'] = 'halt'
        return config, ticker_keys

    # Configuration flags that append to states but do not return / force them
    if '--core' in i_keys:
        core = header_json_parse('--core')
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]
            config['core'] = True
            config['exports'] = core[4]

    if '--test' in i_keys:
        core = header_json_parse('--test')
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]
            config['core'] = True
            config['exports'] = core[4]

    if '--noindex' in i_keys:
        config = add_str_to_dict_key(config, 'state', 'no_index')

    # Exporting of data from metadata.json to dataframe-like file
    if '--export-dataset' in i_keys:
        config = add_str_to_dict_key(config, 'state', 'function run')
        config = add_str_to_dict_key(config, 'run_functions', 'export', type_='list')
        # No functions run, so no tickers should be present. Only metadata keys
        config['exports'] = {"run": True, "fields": ticker_list_to_str(ticker_keys)}


    # Configuration flags that append functions (requires '--function' flag)
    if '--mci' in i_keys:
        config = add_str_to_dict_key(config, 'run_functions', 'mci', type_='list')

    if '--bci' in i_keys:
        config = add_str_to_dict_key(config, 'run_functions', 'bci', type_='list')

    if '--trend' in i_keys:
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'trend', type_='list')

    if '--support_resistance' in i_keys:
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'support_resistance', type_='list')
    
    if ('--sr' in i_keys) or ('--rs' in i_keys) or ('--support_resistance' in i_keys):
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'support_resistance', type_='list')

    if ('--clustered' in i_keys) or ('--clustered_osc' in i_keys):
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'clustered_oscs', type_='list')

    if ('--head_shoulders' in i_keys) or ('--hs' in i_keys):
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'head_shoulders', type_='list')
    
    if ('--corr' in i_keys) or ('--correlation' in i_keys):
        config = add_str_to_dict_key(config, 'run_functions', 'correlation', type_='list')
        if '--short' in i_keys:
            config['duration'] = 'short'
        else:
            config['duration'] = 'long'

    if '--rsi' in i_keys:
        config = add_str_to_dict_key(config, 'run_functions', 'rsi', type_='list')
        config['tickers'] = ticker_list_to_str(ticker_keys)

    if '--macd' in i_keys:
        config = add_str_to_dict_key(config, 'run_functions', 'macd', type_='list')
        config['tickers'] = ticker_list_to_str(ticker_keys)

    if '--relative_strength' in i_keys:
        config = add_str_to_dict_key(config, 'run_functions', 'relative_strength', type_='list')
        config['tickers'] = ticker_list_to_str(ticker_keys)

    if ('--obv' in i_keys) or ('--on_balance_volume' in i_keys):
        config = add_str_to_dict_key(config, 'run_functions', 'obv', type_='list')
        config['tickers'] = ticker_list_to_str(ticker_keys)

    if ('--ma' in i_keys) or ('--moving_average' in i_keys):
        config = add_str_to_dict_key(config, 'run_functions', 'ma', type_='list')
        config['tickers'] = ticker_list_to_str(ticker_keys)


    # Configuration flags that control state outcomes and return immediately after setting
    if '--dev' in i_keys:
        config['state'] = 'dev'
        return config, ticker_keys

    if '--function' in i_keys:
        config = add_str_to_dict_key(config, 'state', 'function run')
        return config, ticker_keys

    if '--prod' in i_keys:
        # default behavior
        config = add_str_to_dict_key(config, 'state', 'run')
        return config, ticker_keys

    if '--r1' in i_keys:
        config = add_str_to_dict_key(config, 'state', 'r1')
        return config, ticker_keys

    if '--r2' in i_keys:
        config = add_str_to_dict_key(config, 'state', 'r2')
        return config, ticker_keys
        
    config = add_str_to_dict_key(config, 'state', 'run')
    return config, ticker_keys


def add_str_to_dict_key(content: dict, key: str, item: str, type_='string'):
    if type_ == 'list':
        content[key].append(item)
        return content
    if len(content[key]) > 0:
        content[key] += f", {item}"
    else:
        content[key] += item 
    return content
    