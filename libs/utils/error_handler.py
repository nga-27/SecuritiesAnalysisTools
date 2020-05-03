import pandas as pd
import numpy as np

from .constants import STANDARD_COLORS

ERROR = STANDARD_COLORS["error"]
NOTE = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]


def has_critical_error(item: dict, e_type: str, misc: dict = None) -> bool:
    """Has Critical Error

    Generic Error checker of items

    Arguments:
        item {dict} -- full data object
        e_type {str} -- error type to compare against

    Keyword Arguments:
        misc {dict} -- currently unimplemented (default: {None})

    Returns:
        bool -- True if error occurred
    """
    if e_type == 'download_data':
        # NaN errors here were handled with 0.1.16 for reformatting data and cleansing of NaN

        for key in item:
            if 'Close' not in item[key]:
                print(
                    f"{ERROR}ERROR DataException: Invalid dataset, contains no list " +
                    f"'Close' for '{key}'.")
                print(f"{NOTE}Exiting...{NORMAL}")
                return True

            if len(item[key]['Close']) == 0:
                print(
                    f"{ERROR}WARNING DataException: Invalid dataset, has no listed data for " +
                    f"'Close' for '{key}'.")
                print(f"{NOTE}Exiting...{NORMAL}")
                return True

            # Assumption is that point or mutual fund NaN errors will be corrected in data.py
            # before this error handler
            nans = list(np.where(pd.isna(item[key]['Close']) == True))[0]
            if len(nans) > 0:
                print("")
                print(
                    f"{ERROR}WARNING DataException: Invalid dataset, contains {len(nans)} " +
                    f"NaN item(s) for 'Close' for '{key}'.")
                print(
                    f"---> This error is likely caused by '{key}' being an invalid or " +
                    f"deprecated ticker symbol.")
                print(f"{NOTE}Exiting...{NORMAL}")
                return True

        return False

    return False
