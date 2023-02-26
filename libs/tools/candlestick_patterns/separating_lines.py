""" separating lines """
from typing import Union
import numpy as np

def separating_lines(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ separating_lines """
    if not body:
        body = 'body'
    thresh = 0.05

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'long' and candle_1['color'] == 'white':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                oc_thr = np.abs(basic_0['Open'] - basic_0['Close']) * thresh
                point1 = basic_0['Open'] - oc_thr
                point2 = basic_0['Open'] + oc_thr
                if basic_1['Open'] <= point2 and basic_1['Open'] >= point1:
                    return {"type": 'bullish', "style": '+'}

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'long' and candle_1['color'] == 'black':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                oc_thr = np.abs(basic_0['Close'] - basic_0['Open']) * thresh
                point1 = basic_0['Open'] - oc_thr
                point2 = basic_0['Open'] + oc_thr
                if basic_1['Open'] <= point2 and basic_1['Open'] >= point1:
                    return {"type": 'bearish', "style": '-'}

    return None
