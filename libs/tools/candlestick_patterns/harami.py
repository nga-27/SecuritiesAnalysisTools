""" harami """
from typing import Union
import numpy as np

def harami(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ harami """
    # pylint: disable=too-many-nested-blocks,too-many-branches
    if not body:
        body = 'body'
    thresh = 0.01

    if trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0['color'] == 'black' and candle_0[body] == 'long':
            candle_1 = trading_candle[1].get('candlestick')
            if candle_1.get('color') == 'white':
                basic_0 = trading_candle[0].get('basic')
                basic_1 = trading_candle[1].get('basic')

                if basic_1.get('High') <= basic_0.get('Open'):
                    if basic_1.get('Low') >= basic_1.get('Close'):
                        hi_low = basic_1.get('High') - basic_1.get('Low')
                        op_clo = np.abs(basic_1.get(
                            'Close') - basic_1.get('Open'))
                        if op_clo <= (hi_low * thresh):
                            return {"type": 'bullish', "style": 'cross-+'}
                        return {"type": 'bullish', "style": "+"}

    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0['color'] == 'white' and candle_0[body] == 'long':
            candle_1 = trading_candle[1].get('candlestick')
            if candle_1.get('color') == 'black':
                basic_0 = trading_candle[0].get('basic')
                basic_1 = trading_candle[1].get('basic')

                if basic_1.get('High') <= basic_0.get('Close'):
                    if basic_1.get('Low') >= basic_1.get('Open'):
                        hi_low = basic_1.get('High') - basic_1.get('Low')
                        op_clo = np.abs(basic_1.get(
                            'Open') - basic_1.get('Close'))
                        if op_clo <= (hi_low * thresh):
                            return {"type": 'bearish', "style": 'cross--'}
                        return {"type": 'bearish', "style": "-"}
    return None
