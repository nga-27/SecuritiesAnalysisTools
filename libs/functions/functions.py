import os
import json
import pprint
import pandas as pd
import numpy as np

from libs.utils import download_data, has_critical_error
from libs.utils import TEXT_COLOR_MAP, STANDARD_COLORS
from libs.utils import generic_plotting
from libs.utils import get_volatility, vq_status_print

from libs.metrics import market_composite_index, bond_composite_index, correlation_composite_index
from libs.metrics import type_composite_index
from libs.metrics import metadata_to_dataset
from libs.metrics import generate_synopsis
from libs.metrics import assemble_last_signals

from libs.tools import get_trendlines, find_resistance_support_lines
from libs.tools import cluster_oscs, RSI, full_stochastic, ultimate_oscillator
from libs.tools import awesome_oscillator, momentum_oscillator
from libs.tools import mov_avg_convergence_divergence, relative_strength, on_balance_volume
from libs.tools import triple_moving_average, moving_average_swing_trade
from libs.tools import bear_bull_power, total_power
from libs.tools import bollinger_bands
from libs.tools import hull_moving_average
from libs.tools import candlesticks

from libs.nasit import generate_fund_from_ledger

from libs.features import feature_detection_head_and_shoulders, analyze_price_gaps

from libs.ui_generation import slide_creator, PDF_creator

TICKER = STANDARD_COLORS["ticker"]
NORMAL = STANDARD_COLORS["normal"]
WARNING = STANDARD_COLORS["warning"]

UP_COLOR = TEXT_COLOR_MAP["green"]
SIDEWAYS_COLOR = TEXT_COLOR_MAP["yellow"]
DOWN_COLOR = TEXT_COLOR_MAP["red"]


def only_functions_handler(config: dict):
    """ Main control function for functions """
    if config.get('run_functions') == ['nf']:
        print(f"Running {TICKER}NASIT{NORMAL} generation...")
    elif (config.get('run_functions') == ['tci']) or (config.get('run_functions') == ['bci']) \
            or (config.get('run_functions') == ['mci']):
        print(
            f"Running {TICKER}{config.get('run_functions')[0].upper()}{NORMAL}...")
    else:
        print(
            f"Running functions: {config['run_functions']} for {TICKER}{config['tickers']}{NORMAL}")

    if 'export' in config['run_functions']:
        # Non-dashed inputs will cause issues beyond export if not returning.
        export_function(config)
        return

    if 'mci' in config['run_functions']:
        mci_function(config)
    if 'bci' in config['run_functions']:
        bci_function(config)
    if 'tci' in config['run_functions']:
        tci_function(config)
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
    if 'stoch' in config['run_functions']:
        stochastic_function(config)
    if 'ultimate' in config['run_functions']:
        ultimate_osc_function(config)
    if 'awesome' in config['run_functions']:
        awesome_osc_function(config)
    if 'momentum' in config['run_functions']:
        momentum_osc_function(config)
    if 'macd' in config['run_functions']:
        macd_function(config)
    if 'relative_strength' in config['run_functions']:
        relative_strength_function(config)
    if 'obv' in config['run_functions']:
        obv_function(config)
    if 'ma' in config['run_functions']:
        ma_function(config)
    if 'swings' in config['run_functions']:
        swing_trade_function(config)
    if 'hull' in config['run_functions']:
        hull_ma_function(config)
    if 'bear_bull' in config['run_functions']:
        bear_bull_function(config)
    if 'total_power' in config['run_functions']:
        total_power_function(config)
    if 'bol_bands' in config['run_functions']:
        bollinger_bands_function(config)
    if 'gaps' in config['run_functions']:
        price_gap_function(config)
    if 'candlestick' in config['run_functions']:
        candlestick_function(config)
    if 'vq' in config['run_functions']:
        vq_function(config)
    if 'nf' in config['run_functions']:
        nasit_generation_function(config)
    if 'nfnow' in config['run_functions']:
        nasit_generation_function(config, print_only=True)
    if 'ledger' in config['run_functions']:
        ledger_function(config)
    if 'synopsis' in config['run_functions']:
        synopsis_function(config)
    if 'last_signals' in config['run_functions']:
        assemble_last_signals_function(config)
    if 'pptx' in config['run_functions']:
        pptx_output_function(config)
    if 'pdf' in config['run_functions']:
        pdf_output_function(config)

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


def tci_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Type Sector'] = config['properties']['Indexes'].get(
        'Type Sector', True)
    type_composite_index(config=config, plot_output=True)


def correlation_index_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})

    timeframe = config.get('duration', 'short')
    temp = {"run": True, "type": timeframe}
    config['properties']['Indexes']['Correlation'] = config['properties']['Indexes'].get(
        'Correlation', temp)
    correlation_composite_index(config=config)


def trends_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Trends of {TICKER}{fund}{NORMAL}...")
            get_trendlines(data[fund], plot_output=True, name=fund)


def support_resistance_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Support & Resistance of {TICKER}{fund}{NORMAL}...")
            find_resistance_support_lines(
                data[fund], plot_output=True, name=fund)


def cluster_oscs_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Clustered Oscillators of {TICKER}{fund}{NORMAL}...")
            cluster_oscs(data[fund], name=fund,
                         plot_output=True, function='all')


def head_and_shoulders_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Head and Shoulders feature detection of {TICKER}{fund}{NORMAL}...")
            feature_detection_head_and_shoulders(
                data[fund], name=fund, plot_output=True)


def export_function(config: dict):
    metadata_to_dataset(config)


def rsi_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"RSI of {TICKER}{fund}{NORMAL}...")
            RSI(data[fund], name=fund, plot_output=True, out_suppress=False)


def stochastic_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Full Stochastic Oscillator of {TICKER}{fund}{NORMAL}...")
            full_stochastic(data[fund], name=fund,
                            plot_output=True, out_suppress=False)


def ultimate_osc_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Ultimate Oscillator of {TICKER}{fund}{NORMAL}...")
            ultimate_oscillator(data[fund], name=fund,
                                plot_output=True, out_suppress=False)


def awesome_osc_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Awesome Oscillator of {TICKER}{fund}{NORMAL}")
            awesome_oscillator(data[fund], name=fund, plot_output=True)


def momentum_osc_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"(Chande) Momentum Oscillator of {TICKER}{fund}{NORMAL}")
            momentum_oscillator(data[fund], name=fund, plot_output=True)


def macd_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"MACD of {TICKER}{fund}{NORMAL}...")
            mov_avg_convergence_divergence(
                data[fund], name=fund, plot_output=True)


def relative_strength_function(config: dict):
    config['tickers'] += ' ^GSPC'
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Relative Strength of {TICKER}{fund}{NORMAL} compared to S&P500...")
            relative_strength(fund, full_data_dict=data,
                              config=config, plot_output=True)


def obv_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"On Balance Volume of {TICKER}{fund}{NORMAL}...")
            on_balance_volume(data[fund], name=fund, plot_output=True)


def ma_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Triple Moving Average of {TICKER}{fund}{NORMAL}...")
            triple_moving_average(data[fund], name=fund, plot_output=True)


def swing_trade_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Triple Moving Average of {TICKER}{fund}{NORMAL}...")
            moving_average_swing_trade(data[fund], name=fund, plot_output=True)


def hull_ma_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Hull Moving Average of {TICKER}{fund}{NORMAL}...")
            hull_moving_average(data[fund], name=fund, plot_output=True)


def bear_bull_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Bear Bull Power Indicator of {TICKER}{fund}{NORMAL}...")
            bear_bull_power(data[fund], name=fund, plot_output=True)


def total_power_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Total Power Indicator of {TICKER}{fund}{NORMAL}...")
            total_power(data[fund], name=fund, plot_output=True)


def bollinger_bands_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Bollinger Bands of {TICKER}{fund}{NORMAL}...")
            bollinger_bands(data[fund], name=fund, plot_output=True)


def price_gap_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Price Gap Analysis of {TICKER}{fund}{NORMAL}...")
            analyze_price_gaps(data[fund], name=fund, plot_output=True)


def candlestick_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Candlestick Analysis of {TICKER}{fund}{NORMAL}...")
            candlesticks(data[fund], name=fund, plot_output=True)


def vq_function(config: dict):
    print(f"Volatility & Stop Losses for funds...")
    print(f"")
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            vq = get_volatility(fund, data=data[fund])
            vq_function_print(vq, fund)


def nasit_generation_function(config: dict, print_only=False):
    print(f"Generating Nasit funds...")
    print(f"")
    nasit_file = 'nasit.json'
    if not os.path.exists(nasit_file):
        print(
            f"{WARNING}WARNING: 'nasit.json' not found. Exiting...{NORMAL}")
        return

    with open(nasit_file) as f:
        nasit = json.load(f)
        f.close()

        fund_list = nasit.get('Funds', [])
        nasit_funds = dict()
        for fund in fund_list:
            t_data, has_cash = nasit_get_data(fund, config)
            nasit_funds[fund.get('ticker')] = nasit_extraction(
                fund, t_data, has_cash=has_cash)
            nasit_funds[f"{fund.get('ticker')}_ret"] = nasit_extraction(
                fund, t_data, has_cash=has_cash, by_price=False)

        if print_only:
            for f in nasit_funds:
                if "_ret" not in f:
                    fund = f
                    price = np.round(nasit_funds[f][-1], 2)
                    change = np.round(price - nasit_funds[f][-2], 2)
                    changep = np.round(
                        (price - nasit_funds[f][-2]) / nasit_funds[f][-2] * 100.0, 3)

                    if change > 0.0:
                        color = UP_COLOR
                    elif change < 0.0:
                        color = DOWN_COLOR
                    else:
                        color = NORMAL

                    print("")
                    print(
                        f"{TICKER}{fund}{color}   ${price} (${change}, {changep}%){NORMAL}")
            print("")
            print("")
            return

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


def ledger_function(config: dict):
    generate_fund_from_ledger(config['tickers'])


def synopsis_function(config: dict):
    meta_file = os.path.join("output", "metadata.json")
    if not os.path.exists(meta_file):
        print(
            f"{WARNING}Warning: '{meta_file}' file does not exist. Run main program.{NORMAL}")
        return

    with open(meta_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()

        for fund in m_data:
            if fund != '_METRICS_':
                print("")
                synopsis = generate_synopsis(m_data, name=fund, print_out=True)
                print("")
                if synopsis is None:
                    print(f"{WARNING}Warning: key 'synopsis' not present.{NORMAL}")
                    return


def assemble_last_signals_function(config: dict):
    meta_file = os.path.join("output", "metadata.json")
    if not os.path.exists(meta_file):
        print(
            f"{WARNING}Warning: '{meta_file}' file does not exist. Run main program.{NORMAL}")
        return

    with open(meta_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()

        for fund in m_data:
            if fund != '_METRICS_':
                print("")
                assemble_last_signals(
                    m_data[fund], standalone=True, print_out=True)
                print("")


def pptx_output_function(config: dict):
    meta_file = os.path.join("output", "metadata.json")
    if not os.path.exists(meta_file):
        print(
            f"{WARNING}Warning: '{meta_file}' file does not exist. Run main program.{NORMAL}")
        return

    with open(meta_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()

        t_fund = None
        for fund in m_data:
            if fund != '_METRICS_':
                t_fund = fund

        if t_fund is None:
            print(
                f"{WARNING}No valid fund found for 'pptx_output_function'. Exiting...{NORMAL}")
            return

        if '2y' not in m_data[t_fund]:
            for period in m_data[t_fund]:
                if (period != 'metadata') and (period != 'synopsis'):
                    config['views']['pptx'] = period

        slide_creator(m_data, config=config)
        return


def pdf_output_function(config: dict):
    meta_file = os.path.join("output", "metadata.json")
    if not os.path.exists(meta_file):
        print(
            f"{WARNING}Warning: '{meta_file}' file does not exist. Run main program.{NORMAL}")
        return

    with open(meta_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()

        t_fund = None
        for fund in m_data:
            if fund != '_METRICS_':
                t_fund = fund

        if t_fund is None:
            print(
                f"{WARNING}No valid fund found for 'pptx_output_function'. Exiting...{NORMAL}")
            return

        if '2y' not in m_data[t_fund]:
            for period in m_data[t_fund]:
                if (period != 'metadata') and (period != 'synopsis'):
                    config['views']['pptx'] = period

        PDF_creator(m_data, config=config)
        return


####################################################


def function_data_download(config: dict) -> list:
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return [], []
    return data, fund_list


def vq_function_print(vq: dict, fund: str):
    if not vq:
        return
    last_max = vq.get('last_max', {}).get('Price')
    stop_loss = vq.get('stop_loss')
    latest = vq.get('latest_price')
    stop_status = vq.get('stopped_out')

    mid_pt = (last_max + stop_loss) / 2.0
    amt_latest = latest - stop_loss
    amt_max = last_max - stop_loss
    percent = np.round(amt_latest / amt_max * 100.0, 2)

    if stop_status == 'Stopped Out':
        status_color = DOWN_COLOR
        status_message = "AVOID - Stopped Out"
    elif latest < stop_loss:
        status_color = DOWN_COLOR
        status_message = "AVOID - Stopped Out"
    elif latest < mid_pt:
        status_color = SIDEWAYS_COLOR
        status_message = "CAUTION - Hold"
    else:
        status_color = UP_COLOR
        status_message = "GOOD - Buy / Maintain"

    print(
        f"{TICKER}{fund}{NORMAL} Volatility Quotient (VQ): {vq.get('VQ')}")
    print(f"Current Price: ${latest}")
    print(f"Stop Loss price: ${stop_loss}")
    print(
        f"Most recent high: ${last_max} on {vq.get('last_max', {}).get('Date')}")
    print(f"Status:  {status_color}{status_message}{NORMAL} ({percent}%)")
    print("")


def nasit_get_data(data: dict, config: dict):
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
    return t_data, has_cash


def nasit_extraction(data: dict, ticker_data: list, has_cash=False, by_price=True):
    subs = data.get('makeup', [])
    fund = nasit_build(ticker_data, subs, has_cash=has_cash, by_price=by_price)
    print(
        f"NASIT generation of {TICKER}{data.get('ticker')}{NORMAL} complete.")
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
