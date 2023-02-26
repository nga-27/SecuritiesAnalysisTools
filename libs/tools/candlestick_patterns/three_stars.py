""" three stars """
from typing import Union
import numpy as np

def three_stars_in_the_south(trading_candle: list,
                             body: Union[str, None] = None) -> Union[dict, None]:
    """ three stars in the south """
    # pylint: disable=too-many-locals,too-many-nested-blocks
    if not body:
        body = 'body'
    shadow_ratio = 1.6
    oc_shadow_ratio = 1.03
    thresh = 0.01
    op_thresh = 0.2

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black' and \
                candle_0['shadow_ratio'] >= shadow_ratio:
            basic_0 = trading_candle[0]['basic']
            hi_op = basic_0['High'] - basic_0['Open']
            oc_thr = np.abs(basic_0['Close'] - basic_0['Open']) * thresh

            if hi_op <= oc_thr:
                candle_1 = trading_candle[1]['candlestick']
                if candle_1[body] == 'short' and candle_1['color'] == 'black':
                    basic_1 = trading_candle[1]['basic']
                    op_point = ((basic_0['Open'] - basic_0['Close']) * op_thresh) + basic_0['Close']

                    if (basic_1['Open'] < op_point) and \
                        (basic_1['Open'] > basic_0['Close']) and \
                            (basic_1['Close'] < basic_0['Close']) and \
                            (basic_1['Low'] > basic_0['Low']):
                        candle_2 = trading_candle[2]['candlestick']

                        if candle_2['shadow_ratio'] <= oc_shadow_ratio and \
                                candle_2['color'] == 'black' and candle_2[body] == 'short':
                            basic_2 = trading_candle[2]['basic']
                            mid_pt = (
                                (basic_1['Open'] - basic_1['Close']) * 0.5) + basic_1['Close']
                            if basic_2['Open'] < mid_pt and basic_2['Close'] < basic_1['Close']:
                                return {"type": 'bullish', "style": "in the south +"}
    return None
