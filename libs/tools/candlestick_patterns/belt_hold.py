""" belt hold """
from typing import Union

def belt_hold(trading_candle: list, _: Union[str, None] = None) -> Union[dict, None]:
    """ belt hold """
    thresh = 0.005
    if trading_candle[0].get('trend') == 'below':
        candle = trading_candle[0].get('candlestick')
        if candle.get('color') == 'white':
            basic = trading_candle[0].get('basic')
            high = basic.get('High')
            _open = basic.get('Open')
            low = basic.get('Low')
            hl_thr = (high - low) * thresh
            op_low = _open - low
            if (op_low <= hl_thr) and (high > basic.get('Close')):
                return {"type": 'bullish', "style": '+'}

    if trading_candle[0].get('trend') == 'above':
        candle = trading_candle[0].get('candlestick')
        if candle.get('color') == 'black':
            basic = trading_candle[0].get('basic')
            high = basic.get('High')
            _open = basic.get('Open')
            low = basic.get('Low')
            hl_thr = (high - low) * (1.0 - thresh)
            op_low = _open - low
            if (op_low >= hl_thr) and (low < basic.get('Close')):
                return {"type": 'bearish', "style": '-'}
    return None
