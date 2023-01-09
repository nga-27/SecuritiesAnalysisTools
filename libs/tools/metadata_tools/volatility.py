import os
from typing import Tuple, List

import numpy as np
from intellistop import IntelliStop, VFStopsResultType

from libs.utils import INDEXES, volatility_factor_plot


def get_volatility(ticker_str: str, **kwargs) -> dict:
    """Get Volatility

    Arguments:
        ticker_str {str} -- ticker of fund

    Returns:
        dict -- volatility quotient data object
    """
    volatility_factor = {}
    ticker_str = ticker_str.upper()

    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', False)

    stops = IntelliStop()
    vf_data = stops.run_analysis_for_ticker(ticker_str)
    close = stops.return_data(ticker_str)
    dates = stops.return_data(ticker_str, key='__full__').get('Date', [])

    volatility_factor = {
        "VF": np.round(vf_data.vf.curated, 3),
        "stop_loss": np.round(vf_data.stop_loss.curated, 2),
        "latest_price": close[-1],
        "last_max": {
            "Date": vf_data.current_status.max_price_date,
            "Price": np.round(vf_data.current_status.max_price, 2)
        },
        "stopped_out": "OK" \
            if vf_data.current_status.status.value != "stopped_out" else "stopped_out",
        "real_status": vf_data.current_status.status.value
    }

    if vf_data.current_status.status.value == "stopped_out":
        volatility_factor['stop_loss'] = 0.0
    
    status, color = volatility_factor_status_print(vf_data.current_status.status.value)
    volatility_factor['status'] = {'status': status, 'color': color}

    if not out_suppress:
        green_zone, yellow_zone, red_zone = create_zones(close, vf_data)
        min_value = min(
            [
                min(min(vf_obj.stop_loss_line) for vf_obj in vf_data.data_sets),
                min(close)
            ]
        )
        range_value = max(close) - min_value

        status_string = f"{ticker_str} is currently in a green zone. BUY."
        status_color = 'green'
        if vf_data.current_status.status.value == 'stopped_out':
            status_string = f"{ticker_str} is currently STOPPED OUT. SELL / wait for a re-entry signal."
            status_color = 'red'
        elif vf_data.current_status.status.value == 'caution_zone':
            status_string = f"{ticker_str} is currently in a caution state. HOLD."
            status_color = 'yellow'

        modified_name = INDEXES.get(ticker_str, ticker_str)
        title = f"{modified_name} - Stop Loss Analysis"
        filename = os.path.join(f"{ticker_str}", f"stop_losses_{ticker_str}.png")

        volatility_factor_plot(close, dates, vf_data, green_zone, red_zone, yellow_zone,
            range_value, min_value, text_str=status_string, str_color=status_color, title=title,
            filename=filename, save_fig=(not plot_output))

    return volatility_factor


def volatility_factor_status_print(vf_data_status: str) -> Tuple[str, str]:
    """VF Status Print

    Arguments:
        vf_data_status {dict} -- volatility quotient data object
        fund {str} -- fund name

    Returns:
        Tuple[str, str] -- status message, status color
    """
    if vf_data_status == "stopped_out":
        status_color = 'red'
        status_message = "AVOID - Stopped Out"
    elif vf_data_status == "caution_zone":
        status_color = 'yellow'
        status_message = "CAUTION - Hold"
    else:
        status_color = 'green'
        status_message = "GOOD - Buy / Maintain"

    return status_message, status_color


def create_zones(close: list, vf_data: VFStopsResultType) -> Tuple[
    List[List[int]], List[List[int]], List[List[int]]]:
    """create_zones

    Return green, yellow, and red zone lists of indexes where they exist on a 5y plot

    Args:
        close (list): price list (either "Close" or "Adj Close")
        vf_data (VFStopsResultType): 

    Returns:
        Tuple[List[List[int]], List[List[int]], List[List[int]]]: green, yellow, red
    """
    green_zones = [vf_obj.time_index_list for vf_obj in vf_data.data_sets]
    temp_concat = []
    for array in green_zones:
        temp_concat.extend(array)
    red_zones = []
    red_one = []
    for i in range(len(close)):
        if i not in temp_concat:
            red_one.append(i)
        else:
            if len(red_one) > 0:
                red_zones.append(red_one)
                red_one = []
    if len(red_one) > 0:
        red_zones.append(red_one)

    yellow_zones = []
    for vf_obj in vf_data.data_sets:
        yellow_one = []
        for i, ind in enumerate(vf_obj.time_index_list):
            if close[ind] < vf_obj.caution_line[i]:
                yellow_one.append(ind)
            else:
                if len(yellow_one) > 0:
                    yellow_zones.append(yellow_one)
                    yellow_one = []
    if len(yellow_one) > 0:
        yellow_zones.append(yellow_one)

    return green_zones, yellow_zones, red_zones
