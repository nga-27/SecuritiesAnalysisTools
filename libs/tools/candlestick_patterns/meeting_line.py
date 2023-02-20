from typing import Union
import numpy as np

def meeting_line(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    thresh = 0.01

    if trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0[body] != 'short' and candle_0['color'] == 'black':
            candle_1 = trading_candle[1].get('candlestick')
            if candle_1['color'] == 'white' and candle_1[body] != 'short':
                basic_1 = trading_candle[1].get('basic')
                basic_0 = trading_candle[0].get('basic')
                hl_thr = (basic_1.get('High') - basic_1.get('Low')) * thresh
                cl_cl = np.abs(basic_0.get('Close') - basic_1.get('Close'))
                if cl_cl <= hl_thr:
                    return {"type": 'bullish', "style": "+"}

    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0[body] != 'short' and candle_0['color'] == 'white':
            candle_1 = trading_candle[1].get('candlestick')
            if candle_1['color'] == 'black' and candle_1[body] != 'short':
                basic_1 = trading_candle[1].get('basic')
                basic_0 = trading_candle[0].get('basic')
                hl_thr = (basic_1.get('High') - basic_1.get('Low')) * thresh
                cl_cl = np.abs(basic_0.get('Close') - basic_1.get('Close'))
                if cl_cl <= hl_thr:
                    return {"type": 'bearish', "style": "-"}
    return None
