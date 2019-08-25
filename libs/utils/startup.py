import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os 
import shutil
import glob
import time
import json 

def start_header(update_release: str='2019-06-04', version: str='0.1.01', default='VTI', options: str=None) -> dict:
    print(" ")
    print("----------------------------------")
    print("-   Securities Analysis Tools    -")
    print("-                                -")
    print("-            nga-27              -")
    print("-                                -")
    print(f"-       version: {version}          -")
    print(f"-       updated: {update_release}      -")
    print("----------------------------------")
    print(" ")

    time.sleep(1)
    config = dict()

    if options is not None:
        x = input("Enter ticker symbols (e.g. 'aapl MSFT') and tags (see --options): ")
    else:
        x = input("Enter ticker symbols (e.g. 'aapl MSFT'): ")

    config['version'] = version
    config['date_release'] = update_release

    config['state'] = 'run'
    config['period'] = '2y'
    config['interval'] = '1d'
    config['properties'] = {}
    config['core'] = False
    config['tickers'] = ''

    if options is not None:
        config, x = header_options_parse(x, config)
        if config['state'] == 'halt':
            return config
        if config['state'] == 'function':
            return config

    x = remove_whitespace_str(x)
    if (x == '') and (config['core'] == False):
        # Default (hitting enter)
        config['tickers'] = default

    else:
        if x != '':
            config['tickers'] += f" {x}"
        if config['core'] == False:
            config['tickers'] = x
            config['tickers'] = config['tickers'].strip()
            if "'" in x:
                spl = x.split("'")
                config['tickers'] = spl[1]        
    
    config['tickers'] = config['tickers'].upper()
    ticker_print = ''

    # whitespace fixing on input strings
    t, config = remove_whitespace(config, default=default)

    if len(t) < 2:
        if config['state'] != 'run_no_index':
            ticker_print += t[0] + ' and S&P500'
        else:
            ticker_print += t[0]
    else:
        for i in range(len(t)):
            if (config['state'] == 'run_no_index') and (i == len(t)-1):
                ticker_print += t[i]
            else:
                if t[i] != '':
                    ticker_print += t[i] + ', '
        if config['state'] != 'run_no_index':
            ticker_print += 'and S&P500'
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


def header_json_parse(input_str: str, key: str) -> list:
    if key not in input_str:
        return None

    json_path = ''
    if key == '--core':
        json_path = 'core.json'
    if key == '--test':
        json_path = 'test.json'

    if os.path.exists(json_path):
        tickers = ''
        with open(json_path) as json_file:
            core = json.load(json_file)
            for i in range(len(core['Ticker Symbols'])-1):
                tickers += core['Ticker Symbols'][i] + ' '
            tickers += core['Ticker Symbols'][len(core['Ticker Symbols'])-1]
            props = core['Properties']
            interval = props['Interval']
            period = props['Period']
    
    else:
        return None

    return [tickers, period, interval, props]


####################################################################

def header_options_parse(input_str: str, config: dict) -> list:
    """ Input flag handling """

    config['state'] = ''
    config['run_functions'] = ''
    if '--options' in input_str:
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
        return config, input_str

    # Configuration flags that append to states but do not return / force them
    if '--core' in input_str:
        core = header_json_parse(input_str, '--core')
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]
            config['core'] = True
            output_str = input_str.replace('--core', '')
            input_str = output_str

    if '--test' in input_str:
        core = header_json_parse(input_str, '--test')
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]
            config['core'] = True
            output_str = input_str.replace('--test', '')
            input_str = output_str

    if '--noindex' in input_str:
        output_str = input_str.replace('--noindex', '')
        config['state'] += '_no_index'
        input_str = output_str


    # Configuration flags that append functions (requires '--function' flag)
    if '--mci' in input_str:
        output_str = input_str.replace('--mci', '')
        config['run_functions'] += ' mci'
        input_str = output_str

    if '--bci' in input_str:
        output_str = input_str.replace('--bci', '')
        config['run_functions'] += ' bci'
        input_str = output_str

    if '--trend' in input_str:
        output_str = input_str.replace('--trend', '')
        ticker_str = output_str.replace('--function', '')
        config['tickers'] = ticker_str
        config['run_functions'] += ' trend'
        input_str = output_str

    # Configuration flags that control state outcomes and return immediately after setting
    if '--dev' in input_str:
        output_str = input_str.replace('--dev', '')
        config['state'] = 'dev'
        return config, output_str

    if '--function' in input_str:
        output_str = input_str.replace('--function', '')
        config['state'] = 'function run'
        return config, output_str

    if '--prod' in input_str:
        # default behavior
        output_str = input_str.replace('--prod', '')
        config['state'] = 'run' + config['state']
        return config, output_str

    if '--r1' in input_str:
        output_str = input_str.replace('--r1', '')
        config['state'] = 'r1'
        return config, output_str

    if '--r2' in input_str:
        output_str = input_str.replace('--r2', '')
        config['state'] = 'r2'
        return config, output_str

    # HAS TO BE LAST! Error catch-all for any '--' inputs
    if '--' in input_str:
        print(f"Error 400: Bad / unknown request of input string of '{input_str}''. Aborting...")
        config['state'] = 'halt'
        return config, input_str
        
    config['state'] = 'run' + config['state']
    return config, input_str