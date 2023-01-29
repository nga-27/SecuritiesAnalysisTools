import numpy as np

from libs.tools import get_volatility
from libs.functions.sub_functions.utils import (
    NORMAL, UP_COLOR, DOWN_COLOR, SIDEWAYS_COLOR, TICKER, function_data_download
)


def vf_function_print(fund: str):
    volatility_factor = get_volatility(fund)
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


def vf_function(config: dict):
    print(f"Volatility & Stop Losses for funds...")
    print(f"")
    _, fund_list = function_data_download(config, fund_list_only=True)
    for fund in fund_list:
        vf_function_print(fund)