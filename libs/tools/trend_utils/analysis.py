""" Analysis Utilities """
import pandas as pd
from scipy.stats import linregress

from libs.utils import dates_convert_from_index


def generate_analysis(fund: pd.DataFrame,
                      x_list: list,
                      y_list: list,
                      len_list: list,
                      color_list: list) -> list:
    """Generate Analysis

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        x_list {list} -- list of x-value lists
        y_list {list} -- list of y-value lists
        len_list {list} -- list of trendline lengths
        color_list {list} -- list of colors, associated with each trendline

    Returns:
        list -- list of analysis data objects
    """
    analysis = []

    for i, x_val in enumerate(x_list):
        sub = {}
        sub['length'] = len(x_val)
        sub['color'] = color_list[i]

        reg = linregress(x_val[0:3], y=y_list[i][0:3])
        sub['slope'] = reg[0]
        sub['intercept'] = reg[1]

        sub['start'] = {}
        sub['start']['index'] = x_val[0]
        sub['start']['date'] = fund.index[x_val[0]].strftime("%Y-%m-%d")

        sub['end'] = {}
        sub['end']['index'] = x_val[len(x_val)-1]
        sub['end']['date'] = fund.index[x_val[len(x_val)-1]].strftime("%Y-%m-%d")

        sub['term'] = len_list[i]
        if sub['slope'] < 0:
            sub['type'] = 'bear'
        else:
            sub['type'] = 'bull'

        sub['x'] = {}
        sub['x']['by_date'] = dates_convert_from_index(fund, [x_val], to_str=True)
        sub['x']['by_index'] = x_val

        if sub['end']['index'] == len(fund['Close'])-1:
            sub['current'] = True
        else:
            sub['current'] = False

        sub = get_attribute_analysis(fund, x_val, y_list[i], sub)

        analysis.append(sub)

    return analysis


def get_attribute_analysis(fund: pd.DataFrame, x_list: list, y_list: list, content: dict) -> dict:
    """Attribute Analysis

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        x_list {list} -- list of trendline x values
        y_list {list} -- list of trendline y values
        content {dict} -- trendline content data object

    Returns:
        dict -- trendline content data object
    """
    # pylint: disable=too-many-locals
    touches = []
    if fund['Close'][x_list[0]] >= y_list[0]:
        state = 'above'
    else:
        state = 'below'

    for i, x_val in enumerate(x_list):
        if state == 'above':
            if fund['Close'][x_val] < y_list[i]:
                state = 'below'
                touches.append(
                    {
                        'index': x_val,
                        'price': fund['Close'][x_val],
                        'type': 'cross',
                        'state': 'below'
                    }
                )
            if fund['Close'][x_val] == y_list[i]:
                touches.append(
                    {
                        'index': x_val,
                        'price': fund['Close'][x_val],
                        'type': 'touch',
                        'state': 'above'
                    }
                )

        else:
            if fund['Close'][x_val] >= y_list[i]:
                state = 'above'
                touches.append(
                    {
                        'index': x_val,
                        'price': fund['Close'][x_val],
                        'type': 'cross',
                        'state': 'above'
                    }
                )
            if fund['Close'][x_val] == y_list[i]:
                touches.append(
                    {
                        'index': x_val,
                        'price': fund['Close'][x_val],
                        'type': 'touch',
                        'state': 'below'
                    }
                )

    content['test_line'] = touches

    valid = []
    broken = []
    if content['type'] == 'bull':
        # trendline will have positive slope. 'above' is valid, 'below' is broken.
        v_start_index = x_list[0]
        v_stop_index = x_list[0]
        b_start_index = x_list[0]
        b_stop_index = x_list[0]
        state = 'above'

        for touch in touches:
            if touch['type'] == 'cross' and touch['state'] == 'below':
                # End of a valid period
                v_stop_index = touch['index'] - 1 if touch['index'] != 0 else x_list[0]
                valid_spot = {'start': {}, 'end': {}}
                valid_spot['start']['index'] = v_start_index
                valid_spot['start']['date'] = fund.index[v_start_index].strftime("%Y-%m-%d")
                valid_spot['end']['index'] = v_stop_index
                valid_spot['end']['date'] = fund.index[v_stop_index].strftime("%Y-%m-%d")
                valid.append(valid_spot)
                b_start_index = touch['index']
                state = 'below'

            if touch['type'] == 'cross' and touch['state'] == 'above':
                # End of a broken period
                b_stop_index = touch['index'] - 1 if touch['index'] != 0 else x_list[0]
                broken_spot = {'start': {}, 'end': {}}
                broken_spot['start']['index'] = b_start_index
                broken_spot['start']['date'] = fund.index[b_start_index].strftime("%Y-%m-%d")
                broken_spot['end']['index'] = b_stop_index
                broken_spot['end']['date'] = fund.index[b_stop_index].strftime("%Y-%m-%d")
                broken.append(broken_spot)
                v_start_index = touch['index']
                state = 'above'

        # End state of trend line
        if state == 'above':
            v_stop_index = x_list[len(x_list)-1]
            valid_spot = {'start': {}, 'end': {}}
            valid_spot['start']['index'] = v_start_index
            valid_spot['start']['date'] = fund.index[v_start_index].strftime("%Y-%m-%d")
            valid_spot['end']['index'] = v_stop_index
            valid_spot['end']['date'] = fund.index[v_stop_index].strftime("%Y-%m-%d")
            valid.append(valid_spot)

        else:
            b_stop_index = x_list[len(x_list)-1]
            broken_spot = {'start': {}, 'end': {}}
            broken_spot['start']['index'] = b_start_index
            broken_spot['start']['date'] = fund.index[b_start_index].strftime("%Y-%m-%d")
            broken_spot['end']['index'] = b_stop_index
            broken_spot['end']['date'] = fund.index[b_stop_index].strftime("%Y-%m-%d")
            broken.append(broken_spot)

    else:
        # trendline will have negative slope. 'below' is valid, 'above' is broken.
        v_start_index = x_list[0]
        v_stop_index = x_list[0]
        b_start_index = x_list[0]
        b_stop_index = x_list[0]
        state = 'below'

        for touch in touches:
            if touch['type'] == 'cross' and touch['state'] == 'above':
                # End of a valid period
                v_stop_index = touch['index'] - \
                    1 if touch['index'] != 0 else x_list[0]
                valid_spot = {'start': {}, 'end': {}}
                valid_spot['start']['index'] = v_start_index
                valid_spot['start']['date'] = fund.index[v_start_index].strftime("%Y-%m-%d")
                valid_spot['end']['index'] = v_stop_index
                valid_spot['end']['date'] = fund.index[v_stop_index].strftime("%Y-%m-%d")
                valid.append(valid_spot)
                b_start_index = touch['index']
                state = 'above'

            if touch['type'] == 'cross' and touch['state'] == 'below':
                # End of a broken period
                b_stop_index = touch['index'] - \
                    1 if touch['index'] != 0 else x_list[0]
                broken_spot = {'start': {}, 'end': {}}
                broken_spot['start']['index'] = b_start_index
                broken_spot['start']['date'] = fund.index[b_start_index].strftime("%Y-%m-%d")
                broken_spot['end']['index'] = b_stop_index
                broken_spot['end']['date'] = fund.index[b_stop_index].strftime("%Y-%m-%d")
                broken.append(broken_spot)
                v_start_index = touch['index']
                state = 'below'

        # End state of trend line
        if state == 'below':
            v_stop_index = x_list[len(x_list)-1]
            valid_spot = {'start': {}, 'end': {}}
            valid_spot['start']['index'] = v_start_index
            valid_spot['start']['date'] = fund.index[v_start_index].strftime("%Y-%m-%d")
            valid_spot['end']['index'] = v_stop_index
            valid_spot['end']['date'] = fund.index[v_stop_index].strftime("%Y-%m-%d")
            valid.append(valid_spot)

        else:
            b_stop_index = x_list[len(x_list)-1]
            broken_spot = {'start': {}, 'end': {}}
            broken_spot['start']['index'] = b_start_index
            broken_spot['start']['date'] = fund.index[b_start_index].strftime("%Y-%m-%d")
            broken_spot['end']['index'] = b_stop_index
            broken_spot['end']['date'] = fund.index[b_stop_index].strftime("%Y-%m-%d")
            broken.append(broken_spot)

    content['valid_period'] = valid
    content['broken_period'] = broken

    return content
