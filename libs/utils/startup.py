""" startup script utility """
import os
import time
import json
from datetime import datetime
from typing import Tuple

from .constants import TEXT_COLOR_MAP, STANDARD_COLORS, LOGO_COLORS

OUTLINE_COLOR = TEXT_COLOR_MAP["blue"]
NORMAL = STANDARD_COLORS["normal"]
AUTHOR_COLOR = TEXT_COLOR_MAP["purple"]

OPT_TITLE_COLOR = TEXT_COLOR_MAP["green"]
OPT_NAME_COLOR = TEXT_COLOR_MAP["cyan"]

MAIN = LOGO_COLORS["main"]
OTHER = LOGO_COLORS["other"]
COPYWRITE = LOGO_COLORS["copywrite"]


def start_header(**kwargs) -> dict:
    """Primary User Input Controller

    Optional Args:
        update_release {str} -- latest date of software release (default: {'2020-05-03'})
        version {str} -- latest release version number (default: {0.2.02})
        default {str} -- default ticker when none given (default: {'VTI'})

    Returns:
        dict -- [description]
    """
    update_release = kwargs.get('update_release', '2023-01-31')
    version = kwargs.get('version', '1.0.0')
    default = kwargs.get('default', 'VTI')

    print(" ")
    print(f"{OUTLINE_COLOR}----------------------------------")
    print(f"-{NORMAL}   Securities Analysis Tools    {OUTLINE_COLOR}-")
    print("-                                -")
    print(f"-{AUTHOR_COLOR}            nga-27              {OUTLINE_COLOR}-")
    print("-                                -")
    print(f"-{NORMAL}       version: {version}          {OUTLINE_COLOR}-")
    print(f"-{NORMAL}       updated: {update_release}      {OUTLINE_COLOR}-")
    print(f"----------------------------------{NORMAL}")
    print(" ")

    time.sleep(1)
    config = {}

    input_str = input("Enter ticker symbols (e.g. 'aapl MSFT') and tags (see --options): ")

    config['version'] = version
    config['date_release'] = update_release

    config['state'] = 'run'
    config['period'] = ['2y']
    config['interval'] = ['1d']
    config['properties'] = {}
    config['core'] = False
    config['tickers'] = ''
    config['exports'] = {"run": False, "fields": []}
    config['views'] = {"pptx": '2y'}
    config['year'] = datetime.now().strftime('%Y')

    config, list_of_tickers = header_options_parse(input_str, config)

    if config['state'] == 'halt':
        return config
    if config['state'] == 'function':
        return config

    if len(list_of_tickers) == 0 and not config['core']:
        # Default (hitting enter)
        config['tickers'] = default

    else:
        if not config['core']:
            config['tickers'] = ' '.join(list_of_tickers)
            config['tickers'] = config['tickers'].strip()

    config['tickers'] = config['tickers'].upper()
    ticker_print = ''

    # whitespace fixing on input strings
    ticker_list, config = remove_whitespace(config, default=default)

    if len(ticker_list) < 2:
        if 'no_index' not in config['state']:
            ticker_print += ticker_list[0] + ', S&P500, and 3mo-TBILL'
        else:
            ticker_print += ticker_list[0]

    else:
        ticker_print = ', '.join(ticker_list)
        if 'no_index' not in config['state']:
            ticker_print += ', S&P500, and 3mo-TBILL'

    config['ticker print'] = ticker_print
    print(" ")
    return config


def remove_whitespace(config: dict, default: str) -> Tuple[list, str]:
    """Remove Whitespace

    In particular, blank inputs, random number of spaces, etc. General cleansing.

    Arguments:
        config {dict} -- controlling dictionary
        default {str} -- default input (usually 'VTI')

    Returns:
        list -- ticker list, ticker string
    """
    ticker_list_2 = config['tickers'].split(' ')
    ticker_list = []
    for ticker_1 in ticker_list_2:
        if ticker_1 != '':
            ticker_list.append(ticker_1)
    if len(ticker_list) == 0:
        config['tickers'] = default
        ticker_list = config['tickers'].split(' ')
    return ticker_list, config


def header_json_parse(key: str) -> list:
    """Header JSON Parse

    Arguments:
        key {str} -- direction to import a specific file

    Returns:
        list -- list of configuration content
    """
    json_path = ''
    if key == '--core':
        json_path = 'core.json'
    if key == '--test':
        json_path = 'test.json'
    if key == '--dataset':
        json_path = 'dataset.json'

    if os.path.exists(json_path):
        tickers = ''
        with open(json_path) as json_file:
            core = json.load(json_file)
            tickers = ' '.join(core['Ticker Symbols'])
            props = core['Properties']
            interval = props['Interval']
            period = props['Period']
            exports = core.get('Exports')
            views = core.get('Views', {})

            if isinstance(period, (str)):
                period = [period]
            if isinstance(interval, (str)):
                interval = [interval]

            for i, inter in enumerate(interval):
                if inter == '1w':
                    interval[i] = '1wk'
                elif inter == '1m':
                    interval[i] = '1mo'

            if views.get('pptx', '') not in period:
                views['pptx'] = period[0]

    else:
        return None

    return [tickers, period, interval, props, exports, views]


def key_parser(input_str: str) -> list:
    """Key Parser

    Arguments:
        input_str {str} -- parse input keys into tickers and input keys

    Returns:
        list -- input keys, tickers
    """
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


def header_options_print(options_read_lines):
    """Header Options Print

    Arguments:
        options_read_lines {file} -- file read in object (.txt)
    """
    print(" ")
    for line in options_read_lines:
        nline = line.replace("\n", "")
        if len(nline) > 0:
            if nline[0].isupper():
                # Pattern 1 - Title lines of options
                nline = f"{OPT_TITLE_COLOR}{nline}{NORMAL}"

            else:
                # Pattern 2 - Individual names colorized
                if '{' in nline:
                    nline = nline.replace("{", f"{OPT_NAME_COLOR}")
                    nline = nline.replace("}", f"{NORMAL}")

        print(nline)
    print(" ")


def logo_renderer():
    """ Render logo from logo.txt file """
    MAIN_LOGO_LINES = 8
    logo_file = os.path.join("resources", "logo.txt")
    if os.path.exists(logo_file):
        fs = open(logo_file, 'r')
        logo_lines = fs.readlines()
        fs.close()
        print(" ")

        for i, line in enumerate(logo_lines):
            if i < MAIN_LOGO_LINES:
                line = line.replace("\n", "")
                line = line.replace("{", f"{OTHER}")
                line = f"{MAIN}{line}{NORMAL}"
            else:
                line = f"{COPYWRITE}{line}{NORMAL}"
            print(line)

        print("\r\n\r\n")
        time.sleep(1)


####################################################################

def header_options_parse(input_str: str, config: dict) -> list:
    """Header Options Parse

    Arguments:
        input_str {str} -- input string from user input
        config {dict} -- controlling dictionary

    Returns:
        list -- config, ticker_keys
    """
    config['state'] = ''
    config['run_functions'] = []
    i_keys, ticker_keys = key_parser(input_str)
    export_now = False

    if '--options' in i_keys:
        options_file = os.path.join("resources", "header_options.txt")
        if os.path.exists(options_file):
            fs = open(options_file, 'r')
            options_read = fs.readlines()
            fs.close()
            header_options_print(options_read)

        else:
            print(f"ERROR - NO {options_file} found.")
            print(" ")

        config['state'] = 'halt'
        return config, ticker_keys

    if ('--quit' in i_keys) or ('--q' in i_keys):
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
            config['views'] = core[5]

    if '--test' in i_keys:
        core = header_json_parse('--test')
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]
            config['core'] = True
            config['exports'] = core[4]
            config['views'] = core[5]

    if '--dataset' in i_keys:
        core = header_json_parse('--dataset')
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]
            config['core'] = True
            config['exports'] = core[4]
            config['views'] = core[5]

    if ('--noindex' in i_keys) or ('--ni' in i_keys):
        config = add_str_to_dict_key(config, 'state', 'no_index')

    if '--suppress' in i_keys:
        config = add_str_to_dict_key(config, 'state', 'suppress_pptx')

    if '--debug' in i_keys:
        config = add_str_to_dict_key(config, 'state', 'debug')

    # Exporting of data from metadata.json to dataframe-like file
    if '--export' in i_keys:
        config = add_str_to_dict_key(config, 'state', 'function run')
        config = add_str_to_dict_key(
            config, 'run_functions', 'export', type_='list')
        # No functions run, so no tickers should be present. Only metadata keys
        config['exports'] = {"run": True,
                             "fields": ' '.join(ticker_keys)}
        export_now = True

    # Only creating a pptx from existing metadata file
    if '--pptx' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'pptx', type_='list')
        config = add_str_to_dict_key(config, 'state', 'function run')
        export_now = True

    if '--pdf' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'pdf', type_='list')
        config = add_str_to_dict_key(config, 'state', 'function run')
        export_now = True

    if export_now:
        return config, ticker_keys

    # Settings for 'intervals' and 'periods'
    if ('--10y' in i_keys) or ('--5y' in i_keys) or \
            ('--2y' in i_keys) or ('--1y' in i_keys):
        config['period'] = []

    if ('--1d' in i_keys) or ('--1w' in i_keys) or ('--1m' in i_keys):
        config['interval'] = []

    if '--10y' in i_keys:
        config['period'].append('10y')
        config['views'] = {'pptx': '10y'}

    if '--5y' in i_keys:
        config['period'].append('5y')
        config['views'] = {'pptx': '5y'}

    if '--2y' in i_keys:
        config['period'].append('2y')
        config['views'] = {'pptx': '2y'}

    if '--1y' in i_keys:
        config['period'].append('1y')
        config['views'] = {'pptx': '1y'}

    if '--1m' in i_keys:
        config['interval'].append('1mo')

    if '--1w' in i_keys:
        config['interval'].append('1wk')

    if '--1d' in i_keys:
        config['interval'].append('1d')

    # Configuration flags that append functions (requires '--function' flag)
    if '--mci' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'mci', type_='list')

    if '--bci' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'bci', type_='list')

    if '--tci' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'tci', type_='list')

    if '--trend' in i_keys:
        config['tickers'] = ' '.join(ticker_keys)
        config = add_str_to_dict_key(
            config, 'run_functions', 'trend', type_='list')

    if '--support_resistance' in i_keys:
        config['tickers'] = ' '.join(ticker_keys)
        config = add_str_to_dict_key(
            config, 'run_functions', 'support_resistance', type_='list')

    if ('--sr' in i_keys) or ('--rs' in i_keys):
        config['tickers'] = ' '.join(ticker_keys)
        config = add_str_to_dict_key(
            config, 'run_functions', 'support_resistance', type_='list')

    if ('--clustered' in i_keys) or ('--clustered_osc' in i_keys) or ('--clusters' in i_keys):
        config['tickers'] = ' '.join(ticker_keys)
        config = add_str_to_dict_key(
            config, 'run_functions', 'clustered_oscs', type_='list')

    if ('--head_shoulders' in i_keys) or ('--hs' in i_keys):
        config['tickers'] = ' '.join(ticker_keys)
        config = add_str_to_dict_key(
            config, 'run_functions', 'head_shoulders', type_='list')

    if ('--corr' in i_keys) or ('--correlation' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'correlation', type_='list')
        if '--short' in i_keys:
            config['duration'] = 'short'
        else:
            config['duration'] = 'long'

    if '--rsi' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'rsi', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--stochastic' in i_keys) or ('--stoch' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'stochastic', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--ultimate' in i_keys) or ('--ult' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'ultimate', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if '--macd' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'macd', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if '--relative_strength' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'relative_strength', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if '--awesome' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'awesome', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if '--momentum' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'momentum', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--obv' in i_keys) or ('--on_balance_volume' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'obv', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--ma' in i_keys) or ('--moving_average' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'moving_average', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--swings' in i_keys) or ('--swing_trade' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'swings', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--hull' in i_keys) or ('--hull_moving_average' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'hull', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--bull_bear' in i_keys) or ('--bear_bull' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'bear_bull', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--total_power' in i_keys) or ('--total' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'total_power', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--bollinger' in i_keys) or ('--bollinger_bands' in i_keys) or \
            ('--bands' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'bollinger_bands', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--roc' in i_keys) or ('--rate_of_change' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'rate_of_change', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--kst' in i_keys) or ('--know_sure_thing' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'know_sure_thing', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--atr' in i_keys) or ('--average_true_range' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'average_true_range', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--adx' in i_keys) or ('--average_directional_index' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'adx', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--sar' in i_keys) or ('--parabolic_sar' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'parabolic_sar', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--demand' in i_keys) or ('--demand_index' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'demand_index', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--gaps' in i_keys) or ('--price_gaps' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'gaps', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--candlesticks' in i_keys) or ('--candlestick' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'candlestick', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--comm' in i_keys) or ('--commodity' in i_keys) or ('--cci' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'commodity', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--alpha' in i_keys) or ('--beta' in i_keys) or ('--risk' in i_keys) or \
        ('--sharpe' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'alpha', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--vf' in i_keys) or ('--stop_loss' in i_keys) or ('--volatility_factor' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'vf', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--nasit_funds' in i_keys) or ('--nf' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'nasit_funds', type_='list')

    if '--nf_now' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'nf_now', type_='list')

    if '--ledger' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'ledger', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if '--metadata' in i_keys:
        config = add_str_to_dict_key(
            config, 'run_functions', 'metadata', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--synopsis' in i_keys) or ('--syn' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'synopsis', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--last' in i_keys) or ('--last_signals' in i_keys):
        config = add_str_to_dict_key(
            config, 'run_functions', 'last_signals', type_='list')
        config['tickers'] = ' '.join(ticker_keys)

    if ('--function' in i_keys) or ('--f' in i_keys):
        config = add_str_to_dict_key(config, 'state', 'function run')
        return config, ticker_keys

    if '--prod' in i_keys:
        # default behavior
        config = add_str_to_dict_key(config, 'state', 'run')
        return config, ticker_keys

    config = add_str_to_dict_key(config, 'state', 'run')
    return config, ticker_keys


def add_str_to_dict_key(content: dict, key: str, item: str, type_='string') -> dict:
    """Add String to Dictionary Key

    Arguments:
        content {dict} -- dictionary to add keys to
        key {str} -- key to append to
        item {str} -- item to add to content[key]

    Keyword Arguments:
        type_ {str} -- to either append to (list) or concatenate to string (default: {'string'})

    Returns:
        dict -- modified content
    """
    if type_ == 'list':
        content[key].append(item)
        return content

    if len(content[key]) > 0:
        content[key] += f", {item}"
    else:
        content[key] += item
    return content
