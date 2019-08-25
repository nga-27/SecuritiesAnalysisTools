import pandas as pd 
import numpy as np 

from libs.utils import download_data
from libs.metrics import market_composite_index, bond_composite_index
from libs.tools import get_trendlines_2

def only_functions_handler(config: dict):
    print(f"Running only functions: '{config['run_functions']}'...")

    if 'mci' in config['run_functions']:
        mci_function(config)

    if 'bci' in config['run_functions']:
        bci_function(config)

    if 'trend' in config['run_functions']:
        trends_function(config)


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
    # config['period'] = '2y'
    # config['interval'] = '1d'
    data, fund_list = download_data(config=config)
    print(f"Trends of {config['tickers']}!")
    get_trendlines_2(data)
