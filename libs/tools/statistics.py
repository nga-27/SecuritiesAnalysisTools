import pandas as pd
import numpy as np


def get_high_level_stats(fund: pd.DataFrame) -> dict:
    """Get High Level Stats

    Arguments:
        fund {pd.DataFrame}

    Returns:
        dict -- statistics
    """
    stats = {}

    len_of_fund = len(fund['Close'])
    stats['current_price'] = fund['Close'][len_of_fund-1]

    stats['current_percent_change'] = (
        fund['Close'][len_of_fund-1] - fund['Close'][len_of_fund-2]) /\
        fund['Close'][len_of_fund-2] * 100.0

    stats['current_change'] = fund['Close'][len_of_fund-1] - \
        fund['Close'][len_of_fund-2]

    stats['tabular'] = list(fund['Close'][0:len_of_fund])
    stats['max_close'] = np.round(max(fund['Close']), 2)

    return stats
