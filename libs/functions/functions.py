import os
import json
from types import FunctionType

import pandas as pd
import numpy as np

from libs.utils import download_data, has_critical_error
from libs.utils import TEXT_COLOR_MAP, STANDARD_COLORS
from libs.utils import generic_plotting
from libs.utils import api_sector_match

from libs.metrics import market_composite_index, bond_composite_index, correlation_composite_index
from libs.metrics import type_composite_index
from libs.metrics import metadata_to_dataset
from libs.metrics import generate_synopsis
from libs.metrics import assemble_last_signals

from libs.tools import get_trend_lines, find_resistance_support_lines
from libs.tools import cluster_oscillators, relative_strength_indicator_rsi, full_stochastic, ultimate_oscillator
from libs.tools import awesome_oscillator, momentum_oscillator
from libs.tools import mov_avg_convergence_divergence, relative_strength
from libs.tools import on_balance_volume, demand_index
from libs.tools import triple_moving_average, moving_average_swing_trade
from libs.tools import bear_bull_power, total_power
from libs.tools import bollinger_bands
from libs.tools import hull_moving_average
from libs.tools import candlesticks
from libs.tools import commodity_channel_index
from libs.tools import risk_comparison
from libs.tools import rate_of_change_oscillator
from libs.tools import know_sure_thing
from libs.tools import average_true_range
from libs.tools import average_directional_index, parabolic_sar
from libs.tools import get_api_metadata
from libs.tools import get_volatility

from libs.nasit import generate_fund_from_ledger

from libs.features import feature_detection_head_and_shoulders, analyze_price_gaps

from libs.ui_generation import slide_creator, PDF_creator

TICKER = STANDARD_COLORS["ticker"]
NORMAL = STANDARD_COLORS["normal"]
WARNING = STANDARD_COLORS["warning"]

UP_COLOR = TEXT_COLOR_MAP["green"]
SIDEWAYS_COLOR = TEXT_COLOR_MAP["yellow"]
DOWN_COLOR = TEXT_COLOR_MAP["red"]


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


def export_function(config: dict):
    metadata_to_dataset(config)


def rsi_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"relative_strength_indicator_rsi of {TICKER}{fund}{NORMAL}...")
            relative_strength_indicator_rsi(data[fund], name=fund, plot_output=True,
                out_suppress=False, trendlines=True)


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
            on_balance_volume(data[fund], name=fund,
                              plot_output=True, trendlines=True)


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


def roc_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Rate of Change of {TICKER}{fund}{NORMAL}...")
            rate_of_change_oscillator(data[fund], name=fund, plot_output=True)


def kst_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Know Sure Thing / Summed Rate of Change of {TICKER}{fund}{NORMAL}...")
            know_sure_thing(data[fund], name=fund, plot_output=True)


def atr_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Average True Range (ATR) of {TICKER}{fund}{NORMAL}...")
            average_true_range(data[fund], name=fund, plot_output=True)


def adx_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Average Directional Index (ADX) of {TICKER}{fund}{NORMAL}...")
            average_directional_index(data[fund], name=fund, plot_output=True)


def sar_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Parabolic 'Stop And Reverse' (SAR) of {TICKER}{fund}{NORMAL}...")
            parabolic_sar(data[fund], name=fund, plot_output=True)


def demand_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Demand Index of {TICKER}{fund}{NORMAL}...")
            demand_index(data[fund], name=fund, plot_output=True)


def price_gap_function(config: dict):
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Price Gap Analysis of {TICKER}{fund}{NORMAL}...")
            analyze_price_gaps(data[fund], name=fund, plot_output=True)


def candlestick_function(config: dict):
    print(f"Candlestick patterns for funds...\r\n")
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Candlestick Analysis of {TICKER}{fund}{NORMAL}...")
            candlesticks(data[fund], name=fund, plot_output=True)


def commodity_function(config: dict):
    print(f"Commodity Channel Index for funds...\r\n")
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Commodity Channel Index of {TICKER}{fund}{NORMAL}...")
            commodity_channel_index(data[fund], name=fund, plot_output=True)


def risk_function(config: dict):
    print(f"Risk Factors for funds...\r\n")
    config['tickers'] += ' ^GSPC ^IRX'
    data, fund_list = function_data_download(config)

    for fund in fund_list:
        if fund != '^GSPC' and fund != '^IRX':
            print(
                f"\r\nRisk Factors of {TICKER}{fund}{NORMAL}...")

            meta_fund = get_api_metadata(fund, function='info')
            match_fund, match_data = function_sector_match(
                meta_fund, data[fund], config)

            if match_fund is not None:
                match_data = match_data.get(match_fund, data.get(match_fund))

            risk_comparison(data[fund], data['^GSPC'],
                            data['^IRX'], print_out=True, sector_data=match_data)
            print("------")


def vf_function(config: dict):
    print(f"Volatility & Stop Losses for funds...")
    print(f"")
    data, fund_list = function_data_download(config, fund_list_only=True)
    for fund in fund_list:
        vf = get_volatility(fund)
        vf_function_print(vf, fund)


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
                    m_data[fund], standalone=True, print_out=True, name=fund)
                print("")


def metadata_function(config: dict):
    print(f"Getting Metadata for funds...")
    print(f"")
    _, fund_list = function_data_download(config, fund_list_only=True)
    for fund in fund_list:
        if fund != '^GSPC':
            metadata = get_api_metadata(fund, plot_output=True)
            altman_z = metadata.get('altman_z', {})
            color = TEXT_COLOR_MAP[altman_z.get('color', 'white')]
            print("\r\n")
            print(f"Altman-Z Score: {color}{altman_z['score']}{NORMAL}")
            print("\r\n")


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


def function_data_download(config: dict, **kwargs) -> list:
    fund_list_only = kwargs.get('fund_list_only', False)
    data, fund_list = download_data(config=config, fund_list_only=fund_list_only)
    if fund_list_only:
        # primarily used for VF, which downloads its own data separately.
        return {}, fund_list

    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return {}, []
    return data, fund_list


def function_sector_match(meta: dict, fund_data: pd.DataFrame, config: dict) -> dict:
    match = meta.get('info', {}).get('sector')
    if match is not None:
        fund_len = {
            'length': len(fund_data['Close']),
            'start': fund_data.index[0],
            'end': fund_data.index[
                len(fund_data['Close'])-1],
            'dates': fund_data.index
        }
        match_fund, match_data = api_sector_match(
            match, config, fund_len=fund_len,
            period=config['period'][0], interval=config['interval'][0])

        return match_fund, match_data
    return None, None


def vf_function_print(volatility_factor: dict, fund: str):
    if not volatility_factor:
        return
    last_max = volatility_factor.get('last_max', {}).get('Price')
    stop_loss = volatility_factor.get('stop_loss')
    latest = volatility_factor.get('latest_price')
    real_status = volatility_factor.get('real_status', '')

    if real_status == 'stopped_out':
        status_color = DOWN_COLOR
        status_message = "AVOID - Stopped Out"
    elif real_status == 'caution_zone':
        status_color = SIDEWAYS_COLOR
        status_message = "CAUTION - Hold"
    else:
        status_color = UP_COLOR
        status_message = "GOOD - Buy / Maintain"

    print("\r\n")
    print(f"{TICKER}{fund}{NORMAL} Volatility Factor (VF): {volatility_factor.get('VF')}")
    print(f"Current Price: ${np.round(latest, 2)}")
    print(f"Stop Loss price: ${stop_loss}")
    print(
        f"Most recent high: ${last_max} on {volatility_factor.get('last_max', {}).get('Date')}")
    print(f"Status:  {status_color}{status_message}{NORMAL}")
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

################################################


def run_function(config: dict, function_to_run: FunctionType, **kwargs):
    data, fund_list = function_data_download(config)
    function_str = str(function_to_run.__name__).capitalize()
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"{function_str} of {TICKER}{fund}{NORMAL}...")
            function_to_run(data[fund], plot_output=True, name=fund, **kwargs)


FUNCTION_MAP = {
    'mci': [mci_function],
    'bci': [bci_function],
    'tci': [tci_function],
    'trend': [run_function, get_trend_lines],
    'support_resistance': [run_function, find_resistance_support_lines],
    'clustered_oscs': [run_function, cluster_oscillators, {'function': 'all'}],
    'head_shoulders': [run_function, feature_detection_head_and_shoulders],
    'correlation': correlation_index_function,
    'rsi': rsi_function,
    'stoch': stochastic_function,
    'ultimate': ultimate_osc_function,
    'awesome': awesome_osc_function,
    'momentum': momentum_osc_function,
    'macd': macd_function,
    'relative_strength': relative_strength_function,
    'obv': obv_function,
    'ma': ma_function,
    'swings': swing_trade_function,
    'hull': hull_ma_function,
    'bear_bull': bear_bull_function,
    'total_power': total_power_function,
    'bol_bands': bollinger_bands_function,
    'roc': roc_function,
    'kst': kst_function,
    'gaps': price_gap_function,
    'candlestick': candlestick_function,
    'commodity': commodity_function,
    'atr': atr_function,
    'adx': adx_function,
    'sar': sar_function,
    'demand': demand_function,
    'alpha': risk_function,
    'vf': vf_function,
    'nf': nasit_generation_function,
    'nfnow': nasit_generation_function,
    'ledger': ledger_function,
    'synopsis': synopsis_function,
    'last_signals':  assemble_last_signals_function,
    'metadata': [metadata_function],
    'pptx': pptx_output_function,
    'pdf': pdf_output_function
}


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

    for function in config['run_functions']:
        functions = FUNCTION_MAP[function]
        if len(functions) == 1:
            # Typically a Composite index function
            functions[0](config)
        else:
            # Other functions. Default to kwargs is {}
            keyword_args = {}
            if len(functions) > 2:
                keyword_args = functions[2]
            functions[0](config, functions[1], **keyword_args)
