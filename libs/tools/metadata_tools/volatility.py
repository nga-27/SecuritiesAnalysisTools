from typing import Tuple

import numpy as np
from intellistop import IntelliStop


def get_volatility(ticker_str: str) -> dict:
    """Get Volatility

    Arguments:
        ticker_str {str} -- ticker of fund

    Returns:
        dict -- volatility quotient data object
    """
    volatility_factor = {}
    ticker_str = ticker_str.upper()

    stops = IntelliStop()
    vf_data = stops.run_analysis_for_ticker(ticker_str)
    close = stops.return_data(ticker_str)

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
