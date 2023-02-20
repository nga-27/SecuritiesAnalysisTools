from typing import Union

def ladder(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    shadow_ratio = 2.0
    thresh = 0.1

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] != 'short' and candle_0['color'] == 'black':
            candle_1 = trading_candle[1]['candlestick']
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']
            if candle_1[body] != 'short' and candle_1['color'] == 'black' and \
                basic_1['Open'] < basic_0['Open'] and basic_1['Open'] > basic_0['Close'] and \
                    basic_1['Close'] < basic_0['Close']:
                candle_2 = trading_candle[2]['candlestick']
                basic_2 = trading_candle[2]['basic']
                if candle_2[body] != 'short' and candle_2['color'] == 'black' and \
                    basic_2['Open'] < basic_1['Open'] and \
                        basic_2['Open'] > basic_1['Close'] and \
                        basic_2['Close'] < basic_1['Close']:
                    candle_3 = trading_candle[3]['candlestick']
                    if candle_3[body] == 'short' and candle_3['color'] == 'black' and \
                            candle_3['shadow_ratio'] >= shadow_ratio:
                        basic_3 = trading_candle[3]['basic']
                        oc_thr = (basic_3['Open'] - basic_3['Close']) * thresh
                        cl_low = basic_3['Close'] - basic_3['Low']
                        if (basic_3['Close'] < basic_2['Close']) and (cl_low <= oc_thr):
                            candle_4 = trading_candle[4]['candlestick']
                            if candle_4[body] == 'long' and candle_4['color'] == 'white' and \
                                    trading_candle[4]['basic']['Open'] > basic_3['Open']:
                                return {"type": 'bullish', "style": 'bottom +'}

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] != 'short' and candle_0['color'] == 'white':
            candle_1 = trading_candle[1]['candlestick']
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']
            if candle_1[body] != 'short' and candle_1['color'] == 'white' and \
                basic_1['Open'] > basic_0['Open'] and basic_1['Open'] < basic_0['Close'] and \
                    basic_1['Close'] > basic_0['Close']:
                candle_2 = trading_candle[2]['candlestick']
                basic_2 = trading_candle[2]['basic']
                if candle_2[body] != 'short' and candle_2['color'] == 'white' and \
                    basic_2['Open'] > basic_1['Open'] and \
                        basic_2['Open'] < basic_1['Close'] and \
                        basic_2['Close'] > basic_1['Close']:
                    candle_3 = trading_candle[3]['candlestick']
                    if candle_3[body] == 'short' and candle_3['color'] == 'white' and \
                            candle_3['shadow_ratio'] >= shadow_ratio:
                        basic_3 = trading_candle[3]['basic']
                        oc_thr = (basic_3['Open'] - basic_3['Close']) * thresh
                        cl_low = basic_3['High'] - basic_3['Close']
                        if (basic_3['Close'] > basic_2['Close']) and (cl_low <= oc_thr):
                            candle_4 = trading_candle[4]['candlestick']
                            if candle_4['body'] == 'long' and candle_4['color'] == 'black' and \
                                    trading_candle[4]['basic']['Open'] < basic_3['Open']:
                                return {"type": 'bearish', "style": 'top -'}
    return None
