import pprint

from libs.utils import ProgressBar
from libs.utils import STANDARD_COLORS, TREND_COLORS, EXEMPT_METRICS

NORMAL = STANDARD_COLORS["normal"]
WARNING = STANDARD_COLORS["warning"]
NOTIFY = STANDARD_COLORS["ticker"]
BULL = TREND_COLORS["good"]
BEAR = TREND_COLORS["bad"]


SIGNAL_KEY = 'signals'
SIZE_KEY = 'length_of_data'

INDICATOR_NAMES = [
    "clustered_osc",
    "full_stochastic",
    "rsi",
    "ultimate",
    "awesome",
    "momentum_oscillator",
    "on_balance_volume",
    "moving_average",
    "exp_moving_average",
    "sma_swing_trade",
    "ema_swing_trade",
    "hull_moving_average",
    "macd",
    "candlesticks",
    "bear_bull_power",
    "total_power",
    "bollinger_bands"
]


def assemble_last_signals(meta_sub: dict, lookback: int = 25, **kwargs) -> dict:
    """assemble_last signals

    Look through all indicators of lookback time and list them

    Arguments:
        meta_sub {dict} -- metadata subset "metadata[fund][view]"

    Keyword Arguments:
        lookback {int} -- number of trading periods into past to find signals (default: {5})

    Returns:
        dict -- last signals data object
    """

    standalone = kwargs.get('standalone', False)
    print_out = kwargs.get('print_out', False)
    pbar = kwargs.get('progress_bar')

    metadata = []
    meta_keys = []

    if standalone:
        for key in meta_sub:
            if key not in EXEMPT_METRICS:
                metadata.append(meta_sub[key])
                meta_keys.append(key)
    else:
        metadata = [meta_sub]
        meta_keys.append('')

    increment = 1.0 / float(len(metadata))

    content = {"signals": []}
    for a, sub in enumerate(metadata):
        print(f"metasub keys: {sub.keys()}\r\n")
        content['signals'] = []
        for key in sub:
            if key in INDICATOR_NAMES:
                print(f"sub sub keys: {sub[key].keys()}\r\n")
                if SIGNAL_KEY in sub[key] and SIZE_KEY in sub[key]:
                    start_period = sub[key][SIZE_KEY] - lookback - 1
                    for signal in sub[key][SIGNAL_KEY]:
                        if signal['index'] >= start_period:
                            data = {
                                "type": signal['type'],
                                "indicator": key,
                                "value": signal['value'],
                                "date": signal['date'],
                                "days_ago": (sub[key][SIZE_KEY] - 1 - signal['index'])
                            }
                            content["signals"].append(data)

        content["signals"].sort(key=lambda x: x['days_ago'])

        if pbar is not None:
            pbar.uptick(increment=increment)

        if print_out:
            content_printer(content, meta_keys[a])

    return content


def content_printer(content: dict, meta_key: str):

    print("\r\n")
    print(f"Content for {NOTIFY}{meta_key}\r\n{NORMAL}")
    print(
        f"{NOTIFY}(Ago)\tType\t::\tIndicator\t\t(value/signal)\t\t\t\t\t:: date{NORMAL}")
    print("")
    for sig in content["signals"]:
        if sig['type'] == 'bearish':
            color = BEAR
        else:
            color = BULL

        indicator = sig['indicator'].split('_')
        for i, ind in enumerate(indicator):
            indicator[i] = ind.capitalize()
        indicator = ' '.join(indicator)

        indicator_tabs = '\t'
        if len(indicator) < 16:
            indicator_tabs = '\t\t'
        if len(indicator) < 8:
            indicator_tabs = '\t\t\t'

        value = f"({sig['value']})"
        value_tabs = '\t'
        if len(value) < 40:
            value_tabs = '\t\t'
        if len(value) < 32:
            value_tabs = '\t\t\t'
        if len(value) < 24:
            value_tabs = '\t\t\t\t'
        if len(value) < 16:
            value_tabs = '\t\t\t\t\t'
        if len(value) < 8:
            value_tabs = '\t\t\t\t\t\t'

        string = f"{color}({sig['days_ago']})\t{sig['type'].upper()}\t::\t" + \
            f"{indicator}{indicator_tabs}{value}{value_tabs}:: {sig['date']}{NORMAL}"
        print(string)
