import pandas as pd 
import numpy as np 

from libs.utils import download_data
from libs.metrics import market_composite_index, bond_composite_index
from libs.tools import get_trendlines_2, find_resistance_support_lines

def only_functions_handler(config: dict):
    print(f"Running functions: '{config['run_functions']}' for {config['tickers']}")

    if 'mci' in config['run_functions']:
        mci_function(config)

    if 'bci' in config['run_functions']:
        bci_function(config)

    if 'trend' in config['run_functions']:
        trends_function(config)
    
    if 'support_resistance' in config['run_functions']:
        support_resistance_function(config)


###############################################################################

def mci_function(config: dict):
    if 'properties' not in config.keys():
        config['properties'] = dict()
    if 'Indexes' not in config['properties'].keys():
        config['properties']['Indexes'] = dict()
    if 'Market Sector' not in config['properties']['Indexes'].keys():
        config['properties']['Indexes']['Market Sector'] = True
    market_composite_index(config=config, plot_output=True)


def bci_function(config: dict):
    if 'properties' not in config.keys():
        config['properties'] = dict()
    if 'Indexes' not in config['properties'].keys():
        config['properties']['Indexes'] = dict()
    
    config['properties']['Indexes']['Treasury Bond'] = True
    config['properties']['Indexes']['Corporate Bond'] = True
    config['properties']['Indexes']['International Bond'] = True
    bond_composite_index(config, plot_output=True)


def trends_function(config: dict):
    data, fund_list = download_data(config=config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Trends of {fund}...")
            get_trendlines_2(data[fund])


def support_resistance_function(config: dict):
    data, fund_list = download_data(config=config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Support & Resistance of {fund}...")
            find_resistance_support_lines(data[fund], plot_output=True, name=f"Support Resistance of {fund}")