from typing import Union

def shooting_star(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    ratio = 2.0
    thresh = 0.01

    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            basic_0 = trading_candle[0].get('basic')
            if basic_0.get('Close') < basic_0.get('High'):
                candle_1 = trading_candle[1].get('candlestick')
                if candle_1[body] == 'short' and candle_1['shadow_ratio'] >= ratio:
                    basic_1 = trading_candle[1].get('basic')
                    high = basic_1.get('High')
                    low = basic_1.get('Low')
                    close = basic_1.get('Close')
                    _open = basic_1.get('Open')

                    if (_open > basic_0.get('Close')) and (close > basic_0.get('Close')):
                        hl_thr = (high - low) * thresh
                        cl_low = close - low
                        op_low = _open - low
                        if (cl_low <= hl_thr) or (op_low <= hl_thr):
                            return {"type": 'bearish', "style": '-'}
    return None
