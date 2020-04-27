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

    for sub in metadata:
        print(f"metasub keys: {sub.keys()}")
        for key in sub:
            if key in INDICATOR_NAMES:
                print(f"\r\nKey: {key}\r\n")
                if SIGNAL_KEY in sub[key] and SIZE_KEY in sub[key]:
                    start_period = sub[key][SIZE_KEY] - lookback - 1

    if pbar is not None:
        pbar.uptick(increment=1.0)
    return {}
