import pandas as pd 
import numpy as np 

from libs.utils import download_data, has_critical_error, TEXT_COLOR_MAP
from libs.metrics import market_composite_index, bond_composite_index, correlation_composite_index
from libs.metrics import metadata_to_dataset
from libs.tools import get_trendlines, find_resistance_support_lines, cluster_oscs, RSI
from libs.tools import mov_avg_convergence_divergence, relative_strength, on_balance_volume
from libs.tools import triple_moving_average
from libs.features import feature_detection_head_and_shoulders

ticker_color = TEXT_COLOR_MAP["cyan"]
normal_color = TEXT_COLOR_MAP["white"]

def only_functions_handler(config: dict):
    print(f"Running functions: {config['run_functions']} for {ticker_color}{config['tickers']}{normal_color}")

    if 'export' in config['run_functions']:
        # Non-dashed inputs will cause issues beyond export if not returning.
        export_function(config)
        return

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
    if 'head_shoulders' in config['run_functions']:
        head_and_shoulders_function(config)
    if 'correlation' in config['run_functions']:
        correlation_index_function(config)
    if 'rsi' in config['run_functions']:
        rsi_function(config)
    if 'macd' in config['run_functions']:
        macd_function(config)
    if 'relative_strength' in config['run_functions']:
        relative_strength_function(config)
    if 'obv' in config['run_functions']:
        obv_function(config)
    if 'ma' in config['run_functions']:
        ma_function(config)
    


###############################################################################

def mci_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Market Sector'] = config['properties']['Indexes'].get('Market Sector', True)
    market_composite_index(config=config, plot_output=True)


def bci_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Treasury Bond'] = True
    config['properties']['Indexes']['Corporate Bond'] = True
    config['properties']['Indexes']['International Bond'] = True
    bond_composite_index(config, plot_output=True)


def trends_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Trends of {ticker_color}{fund}{normal_color}...")
            get_trendlines(data[fund], plot_output=True, name=fund)


def support_resistance_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Support & Resistance of {ticker_color}{fund}{normal_color}...")
            find_resistance_support_lines(data[fund], plot_output=True, name=fund)


def cluster_oscs_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Clustered Oscillators of {ticker_color}{fund}{normal_color}...")
            cluster_oscs(data[fund], name=fund, plot_output=True, function='all')


def head_and_shoulders_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Head and Shoulders feature detection of {ticker_color}{fund}{normal_color}...")
            feature_detection_head_and_shoulders(data[fund], name=fund, plot_output=True)


def correlation_index_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})

    timeframe = config.get('duration', 'long')
    temp = {"run": True, "type": timeframe}
    config['properties']['Indexes']['Correlation'] = config['properties']['Indexes'].get('Correlation', temp)
    correlation_composite_index(config=config)


def export_function(config: dict):
    metadata_to_dataset(config)


def rsi_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"RSI of {ticker_color}{fund}{normal_color}...")
            RSI(data[fund], name=fund, plot_output=True, out_suppress=False)


def macd_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"MACD of {ticker_color}{fund}{normal_color}...")
            mov_avg_convergence_divergence(data[fund], name=fund, plot_output=True)


def relative_strength_function(config: dict):
    config['tickers'] += ' ^GSPC'
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Relative Strength of {ticker_color}{fund}{normal_color} compared to S&P500...")
            relative_strength(fund, full_data_dict=data, config=config, plot_output=True)


def obv_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"On Balance Volume of {ticker_color}{fund}{normal_color}...")
            on_balance_volume(data[fund], name=fund, plot_output=True)


def ma_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Triple Moving Average of {ticker_color}{fund}{normal_color}...")
            triple_moving_average(data[fund], name=fund, plot_output=True)



####################################################

def function_data_download(config: dict) -> list:
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return [], []
    return data, fund_list