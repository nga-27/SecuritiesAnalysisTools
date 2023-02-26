""" Trend Utils """
import pandas as pd


def line_extender(fund: pd.DataFrame, x_range: list, reg_vals: list) -> int:
    """Line Extender

    returns the end of a particular trend line. returns 0 if segment should be omitted

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        x_range {list} -- applicable x data points
        reg_vals {list} -- linear regression values

    Returns:
        int -- new endpoint to end the inspected trendline
    """
    slope = reg_vals[0]
    intercept = reg_vals[1]
    max_len = len(fund['Close'])

    if slope > 0.0:
        end_pt = x_range[len(x_range)-1]
        start_pt = x_range[0]
        for i in range(start_pt, end_pt):
            y_val = intercept + slope * i
            if fund['Close'][i] < (y_val * 0.99):
                    # Original trendline was not good enough - omit
                return 0
        # Now that original trendline is good, find ending
        # Since we have 'line_reducer', send the maximum and let reducer fix it
        return max_len

    end_pt = x_range[len(x_range)-1]
    start_pt = x_range[0]
    for i in range(start_pt, end_pt):
        y_val = intercept + slope * i
        if fund['Close'][i] > (y_val * 1.01):
            # Original trend line was not good enough - omit
            return 0

    # Now that original trend line is good, find ending since we have 'line_reducer', send the
    # maximum and let reducer fix it
    return max_len


def line_reducer(fund: pd.DataFrame, last_x_pt: int, reg_vals: list, threshold=0.05) -> int:
    """Line Extender

    returns shortened lines that protrude far away from overall fund price (to not distort plots)

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        last_x_pt {int} -- calculated last x point (from line_extender)
        reg_vals {list} -- linear regression values

    Keyword Arguments:
        threshold {float} -- +/- threshold to see if trend is still valid at last point
                             (default: {0.05})

    Returns:
        int -- new endpoint to end the inspected trend line
    """
    # pylint: disable=chained-comparison
    slope = reg_vals[0]
    intercept = reg_vals[1]
    top_thresh = 1.0 + threshold
    bot_thresh = 1.0 - threshold

    x_pt = last_x_pt
    if x_pt > len(fund['Close']):
        x_pt = len(fund['Close'])

    last_pt = intercept + slope * x_pt
    if last_pt <= (top_thresh * fund['Close'][x_pt-1]) and \
        last_pt >= (bot_thresh * fund['Close'][x_pt-1]):
        return x_pt

    while x_pt-1 > 0 and \
        (last_pt > (top_thresh * fund['Close'][x_pt-1]) or \
            last_pt < (bot_thresh * fund['Close'][x_pt-1])):
        x_pt -= 1
        last_pt = intercept + slope * x_pt

    return x_pt
