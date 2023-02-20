from typing import Union

def stick_sandwich(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    thresh = 0.02
    mf_shadow_ratio = 1.03
    close_thresh = 0.05

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            basic_0 = trading_candle[0]['basic']
            oc_thr = (basic_0['Open'] - basic_0['Close']) * thresh
            cl_low = basic_0['Close'] - basic_0['Low']
            if (cl_low <= oc_thr):
                candle_1 = trading_candle[1]['candlestick']
                if candle_1[body] == 'long' and candle_1['color'] == 'white' and \
                        candle_1['shadow_ratio'] <= mf_shadow_ratio:
                    basic_1 = trading_candle[1]['basic']
                    basic_0 = trading_candle[0]['basic']
                    if (basic_1['Open'] > basic_0['Close']) and \
                            (basic_1['Open'] < basic_0['Open']):
                        candle_2 = trading_candle[2]['candlestick']
                        if candle_2[body] == 'long' and candle_2['color'] == 'black':
                            basic_2 = trading_candle[2]['basic']
                            point1 = ((basic_2['Open'] - basic_2['Close']) * close_thresh) + \
                                basic_2['Close']
                            point2 = basic_2['Close'] - \
                                ((basic_2['Open'] - basic_2['Close']) * close_thresh)
                            if (basic_0['Close'] <= point1) and (basic_0['Close'] >= point2):
                                if basic_2['Open'] > basic_1['Close']:
                                    return {"type": 'bullish', "style": '+'}

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            basic_0 = trading_candle[0]['basic']
            oc_thr = (basic_0['Close'] - basic_0['Open']) * thresh
            cl_low = basic_0['High'] - basic_0['Close']
            if (cl_low <= oc_thr):
                candle_1 = trading_candle[1]['candlestick']
                if candle_1[body] == 'long' and candle_1['color'] == 'black' and \
                        candle_1['shadow_ratio'] <= mf_shadow_ratio:
                    basic_1 = trading_candle[1]['basic']
                    basic_0 = trading_candle[0]['basic']
                    if (basic_1['Open'] > basic_0['Open']) and \
                            (basic_1['Open'] < basic_0['Close']):
                        candle_2 = trading_candle[2]['candlestick']
                        if candle_2[body] == 'long' and candle_2['color'] == 'white':
                            basic_2 = trading_candle[2]['basic']
                            point1 = ((basic_2['Close'] - basic_2['Open']) * close_thresh) + \
                                basic_2['Close']
                            point2 = basic_2['Close'] - \
                                ((basic_2['Close'] - basic_2['Open']) * close_thresh)
                            if (basic_0['Close'] <= point1) and (basic_0['Close'] >= point2):
                                if basic_2['Open'] < basic_1['Close']:
                                    return {"type": 'bearish', "style": '-'}
    return None
