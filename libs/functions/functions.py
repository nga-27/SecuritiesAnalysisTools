import pandas as pd 
import numpy as np 

from libs.utils import download_data, has_critical_error
from libs.metrics import market_composite_index, bond_composite_index
from libs.tools import get_trendlines, find_resistance_support_lines, cluster_oscs

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

    if 'clustered_oscs' in config['run_functions']:
        cluster_oscs_function(config)


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
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return None
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Trends of {fund}...")
            get_trendlines(data[fund])


def support_resistance_function(config: dict):
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return None
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Support & Resistance of {fund}...")
            find_resistance_support_lines(data[fund], plot_output=True, name=fund)


def cluster_oscs_function(config: dict):
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return None
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Clustered Oscillators of {fund}...")
            cluster_oscs(data[fund], name=fund, plot_output=True, function='all')