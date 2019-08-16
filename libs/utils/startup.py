import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os 
import shutil
import glob
import time
import json 

def start_header(update_release: str='2019-06-04', version: str='0.1.01', default='VTI') -> dict:
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

    x = input("Enter ticker symbols (e.g. 'aapl') and tags (see --options): ")

    config['period'] = None
    config['interval'] = None
    config['properties'] = None
    config['state'], x = header_options_parse(x)

    if config['state'] == 'halt':
        return config

    if x == '':
        # Default (hitting enter)
        config['tickers'] = default

    else:
        core = header_core_parse(x)
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]

        else:
            config['tickers'] = x
            if "'" in x:
                spl = x.split("'")
                config['tickers'] = spl[1]        
    
    config['tickers'] = config['tickers'].upper()
    ticker_print = ''
    t = config['tickers'].split(' ')
    if len(t) < 2:
        if config['state'] != 'run_no_index':
            ticker_print += t[0] + ' and ^GSPC'
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
            ticker_print += 'and ^GSPC'
    config['ticker print'] = ticker_print
    print(" ")
    return config 


def header_core_parse(input_str: str) -> list:
    if '--core' not in input_str:
        return None

    if os.path.exists('core.json'):
        tickers = ''
        with open('core.json') as json_file:
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


def header_options_parse(input_str: str) -> list:
    if '--options' in input_str:
        print(" ")
        print("OPTIONS:")
        print(" ")
        print("--core       :     normal operation run with parameters found in core.json")
        print("--r1         :     run release_1.py [FUTURE RELEASE]")
        print("--noindex    :     does not include S&P500 index, omits comparison operations")
        print(" ")
        print("FUNCTIONS:   :     (e.g. '--clustered_osc --macd vti AAPL amzn' ) [FUTURE RELEASE]")
        print(" ")
        print("--clustered_osc    displays plot of oscillator of fund [FUTURE RELEASE]")
        print("--macd             displays plot of moving average convergence/divergence [FUTURE RELEASE]")
        print(" ")
        return ['halt', input_str]

    if '--noindex' in input_str:
        output_str = input_str.replace('--noindex', '')
        return 'run_no_index', output_str

    
    return 'run', input_str