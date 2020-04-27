import pprint

from libs.utils import ProgressBar
from libs.utils import STANDARD_COLORS

NORMAL = STANDARD_COLORS["normal"]
WARNING = STANDARD_COLORS["warning"]

SIGNAL_KEY = 'signals'
SIZE_KEY = 'length_of_data'

INDICATOR_NAMES = [
    "clustered_osc"
]


def assemble_last_signals(meta_sub: dict, lookback: int = 5, **kwargs) -> dict:
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

    if pbar is not None:
        pbar.uptick(increment=1.0)

    if print_out:
        print("\r\n")
        for sig in content["signals"]:
            print(f"({sig['days_ago']}) {sig['type'].upper()} :: {sig['indicator']} " +
                  f"({sig['value']}) :: {sig['date']}")

    return content
