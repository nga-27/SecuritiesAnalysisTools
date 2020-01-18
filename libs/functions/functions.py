import os
import json
import pprint
import pandas as pd
import numpy as np

from libs.utils import download_data, has_critical_error, TEXT_COLOR_MAP
from libs.utils import get_volatility, generic_plotting
from libs.metrics import market_composite_index, bond_composite_index, correlation_composite_index
from libs.metrics import metadata_to_dataset
from libs.tools import get_trendlines, find_resistance_support_lines, cluster_oscs, RSI
from libs.tools import mov_avg_convergence_divergence, relative_strength, on_balance_volume
from libs.tools import triple_moving_average
from libs.features import feature_detection_head_and_shoulders, analyze_price_gaps

ticker_color = TEXT_COLOR_MAP["cyan"]
normal_color = TEXT_COLOR_MAP["white"]
WARNING_COLOR = TEXT_COLOR_MAP["yellow"]


def only_functions_handler(config: dict):
    if config.get('run_functions') == ['nf']:
        print(f"Running {ticker_color}NASIT{normal_color} generation...")
    else:
        print(
            f"Running functions: {config['run_functions']} for {ticker_color}{config['tickers']}{normal_color}")

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
    if 'gaps' in config['run_functions']:
        price_gap_function(config)
    if 'vq' in config['run_functions']:
        vq_function(config)
    if 'nf' in config['run_functions']:
        nasit_generation_function(config)

###############################################################################


def mci_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Market Sector'] = config['properties']['Indexes'].get(
        'Market Sector', True)
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
            print(
                f"Support & Resistance of {ticker_color}{fund}{normal_color}...")
            find_resistance_support_lines(
                data[fund], plot_output=True, name=fund)


def cluster_oscs_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Clustered Oscillators of {ticker_color}{fund}{normal_color}...")
            cluster_oscs(data[fund], name=fund,
                         plot_output=True, function='all')


def head_and_shoulders_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Head and Shoulders feature detection of {ticker_color}{fund}{normal_color}...")
            feature_detection_head_and_shoulders(
                data[fund], name=fund, plot_output=True)


def correlation_index_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})

    timeframe = config.get('duration', 'long')
    temp = {"run": True, "type": timeframe}
    config['properties']['Indexes']['Correlation'] = config['properties']['Indexes'].get(
        'Correlation', temp)
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
            mov_avg_convergence_divergence(
                data[fund], name=fund, plot_output=True)


def relative_strength_function(config: dict):
    config['tickers'] += ' ^GSPC'
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Relative Strength of {ticker_color}{fund}{normal_color} compared to S&P500...")
            relative_strength(fund, full_data_dict=data,
                              config=config, plot_output=True)


def obv_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"On Balance Volume of {ticker_color}{fund}{normal_color}...")
            on_balance_volume(data[fund], name=fund, plot_output=True)


def ma_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Triple Moving Average of {ticker_color}{fund}{normal_color}...")
            triple_moving_average(data[fund], name=fund, plot_output=True)


def price_gap_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Price Gap Analysis of {ticker_color}{fund}{normal_color}...")
            analyze_price_gaps(data[fund], name=fund, plot_output=True)


def vq_function(config: dict):
    print(f"Volatility & Stop Losses for funds...")
    print(f"")
    fund_list = config['tickers'].split(' ')
    for fund in fund_list:
        if fund != '^GSPC':
            vq = get_volatility(fund)
            print(
                f"{ticker_color}{fund}{normal_color} Volatility Quotient (VQ): {vq.get('VQ')}")
            print(f"Current Price: ${vq.get('latest_price')}")
            print(f"Stop Loss price: ${vq.get('stop_loss')}")
            print(
                f"Most recent high: ${vq.get('last_max', {}).get('Price')} on {vq.get('last_max', {}).get('Date')}")
            print("")


def nasit_generation_function(config: dict):
    print(f"Generating Nasit funds...")
    print(f"")
    nasit_file = 'nasit.json'
    if not os.path.exists(nasit_file):
        print(
            f"{WARNING_COLOR}WARNING: 'nasit.json' not found. Exiting...{normal_color}")
        return
    with open(nasit_file) as f:
        nasit = json.load(f)
        fund_list = nasit.get('Funds', [])
        nasit_funds = dict()
        for fund in fund_list:
            nasit_funds[fund.get('ticker')] = nasit_extraction(fund, config)
            nasit_funds[f"{fund.get('ticker')}_ret"] = nasit_extraction(
                fund, config, by_price=False)

        df = pd.DataFrame(nasit_funds)
        out_file = 'output/NASIT.csv'
        df.to_csv(out_file)

        plotable = []
        plotable2 = []
        names = []
        names2 = []
        for f in nasit_funds:
            if '_ret' not in f:
                plotable.append(nasit_funds[f])
                names.append(f)
            else:
                plotable2.append(nasit_funds[f])
                names2.append(f)
        generic_plotting(plotable, legend=names, title='NASIT Passives')
        generic_plotting(plotable2, legend=names2,
                         title='NASIT Passives [Returns]')


####################################################


def function_data_download(config: dict) -> list:
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return [], []
    return data, fund_list


def nasit_extraction(data: dict, config: dict, by_price=True):
    subs = data.get('makeup', [])
    tickers = []
    has_cash = False
    for sub in subs:
        if sub['symbol'] != 'xCASHx':
            tickers.append(sub['symbol'])
        else:
            has_cash = True
    ticker_str = ' '.join(tickers)
    config['period'] = '2y'
    config['tickers'] = ticker_str
    config['ticker print'] = ', '.join(tickers)
    t_data, _ = function_data_download(config)
    fund = nasit_build(t_data, subs, has_cash=has_cash, by_price=by_price)

    print(
        f"NASIT generation of {ticker_color}{data.get('ticker')}{normal_color} complete.")
    print("")
    return fund


def nasit_build(data: dict, makeup: dict, has_cash=False, by_price=True):
    CASH_PERCENT = 0.01
    START_VALUE = 25.0
    deltas = dict()
    data_len = 0

    if by_price:
        key = 'Close'
    else:
        key = 'Adj Close'

    for tick in data:
        deltas[tick] = []
        deltas[tick].append(0.0)
        data_len = len(data[tick][key])
        for i in range(1, data_len):
            diff = (data[tick][key][i] - data[tick]
                    [key][i-1]) / data[tick][key][i-1]
            deltas[tick].append(diff)

    if has_cash:
        DIVISOR = CASH_PERCENT / float(data_len) / 2.0
        deltas['cash'] = [0.0]
        for i in range(1, data_len):
            deltas['cash'].append(DIVISOR)

    new_fund = [0.0] * data_len
    for component in makeup:
        sym = component['symbol']
        amt = component['allocation']
        if sym == 'xCASHx':
            sym = 'cash'
        for i, val in enumerate(deltas[sym]):
            new_fund[i] += val * amt

    new_closes = [START_VALUE]
    for i in range(1, len(new_fund)):
        close = new_closes[-1] * (1.0 + new_fund[i])
        new_closes.append(close)

    return new_closes
