from typing import Union
import numpy as np

def kicking(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    thresh = 0.01

    candle_0 = trading_candle[0]['candlestick']
    candle_1 = trading_candle[1]['candlestick']
    if candle_0[body] == 'long' and \
        candle_0['color'] == 'black' and \
            candle_1[body] == 'long' and \
            candle_1['color'] == 'white':
        basic_0 = trading_candle[0]['basic']
        oc_thr = np.abs(basic_0['Open'] - basic_0['Close']) * thresh
        hi_op = basic_0['High'] - basic_0['Open']
        cl_lo = basic_0['Close'] - basic_0['Low']

        if (hi_op <= oc_thr) and (cl_lo <= oc_thr):
            basic_1 = trading_candle[1]['basic']
            oc_thr = np.abs(basic_1['Open'] - basic_1['Close']) * thresh
            hi_cl = basic_1['High'] - basic_1['Close']
            op_lo = basic_1['Open'] - basic_1['Low']
            if (hi_cl <= oc_thr) and (op_lo <= oc_thr):
                if (basic_0['High'] < basic_1['Low']):
                    return {"type": 'bullish', "style": '+'}

    if candle_0[body] == 'long' and \
        candle_0['color'] == 'white' and \
            candle_1[body] == 'long' and \
            candle_1['color'] == 'black':
        basic_0 = trading_candle[0]['basic']
        oc_thr = np.abs(basic_0['Close'] - basic_0['Open']) * thresh
        hi_op = basic_0['High'] - basic_0['Close']
        cl_lo = basic_0['Open'] - basic_0['Low']

        if (hi_op <= oc_thr) and (cl_lo <= oc_thr):
            basic_1 = trading_candle[1]['basic']
            oc_thr = np.abs(basic_1['Open'] - basic_1['Close']) * thresh
            hi_cl = basic_1['High'] - basic_1['Open']
            op_lo = basic_1['Close'] - basic_1['Low']
            if (hi_cl <= oc_thr) and (op_lo <= oc_thr):
                if (basic_0['Low'] > basic_1['High']):
                    return {"type": 'bearish', "style": '-'}
    return None
