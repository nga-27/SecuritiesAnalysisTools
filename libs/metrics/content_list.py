import pprint

from libs.utils import ProgressBar
from libs.utils import STANDARD_COLORS, TREND_COLORS

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
    "ultimate"
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

    if standalone:
        for key in meta_sub:
            if key != 'metadata' and key != 'synopsis':
                metadata.append(meta_sub[key])
    else:
        metadata = [meta_sub]

    content = {"signals": []}
    for sub in metadata:
        print(f"metasub keys: {sub.keys()}\r\n")
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
        pbar.uptick(increment=1.0)

    if print_out:
        print("\r\n")
        print(f"{NOTIFY}(Periods ago) Type :: Indicator (value/signal) :: date{NORMAL}")
        print("")
        for sig in content["signals"]:
            if sig['type'] == 'bearish':
                string = f"{BEAR}({sig['days_ago']}) {sig['type'].upper()} :: {sig['indicator']} " + \
                    f"({sig['value']}) :: {sig['date']}{NORMAL}"
            else:
                string = f"{BULL}({sig['days_ago']}) {sig['type'].upper()} :: {sig['indicator']} " + \
                    f"({sig['value']}) :: {sig['date']}{NORMAL}"
            print(string)

    return content
