""" hammers """
from typing import Union

def inverted_hammer(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ inverted hammer """
    if not body:
        body = 'body'
    ratio = 2.0
    thresh = 0.01

    if trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = trading_candle[1].get('candlestick')

            if candle_1[body] == 'short' and candle_1['shadow_ratio'] >= ratio:
                basic = trading_candle[1].get('basic')
                high = basic.get('High')
                close = basic.get('Close')
                _open = basic.get('Open')
                low = basic.get('Low')
                hl_thr = (high - low) * thresh
                cl_low = close - low
                op_low = _open - low
                if (cl_low <= hl_thr) or (op_low <= hl_thr):
                    return {"type": 'bullish', "style": '+'}
    return None


def hammer_positive(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ hammer positive """
    if not body:
        body = 'body'
    ratio = 2.0
    thresh = 0.99

    if trading_candle[0].get('trend') == 'below':
        candle = trading_candle[0].get('candlestick')
        if candle[body] == 'short' and candle['shadow_ratio'] >= ratio:
            basic = trading_candle[0].get('basic')
            high = basic.get('High')
            close = basic.get('Close')
            _open = basic.get('Open')
            low = basic.get('Low')
            hl_thr = (high - low) * thresh
            cl_low = close - low
            op_low = _open - low
            if (cl_low >= hl_thr) or (op_low >= hl_thr):
                return {"type": 'bullish', "style": '+'}
    return None
