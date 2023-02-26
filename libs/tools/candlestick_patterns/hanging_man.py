""" hanging man """
from typing import Union

def hanging_man(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ hanging man """
    if not body:
        body = 'body'
    ratio = 2.0
    thresh = 0.99

    if trading_candle[0].get('trend') == 'above':
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
                return {"type": 'bearish', "style": '-'}
    return None
