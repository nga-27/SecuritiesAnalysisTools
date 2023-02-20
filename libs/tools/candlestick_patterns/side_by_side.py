from typing import Union

def side_by_side_white_lines(trading_candle: list,
                             body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    thresh = 0.1
    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            if trading_candle[1]['candlestick']['color'] == 'white':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                if basic_1['Low'] > basic_0['High']:
                    if trading_candle[2]['candlestick']['color'] == 'white':
                        basic_2 = trading_candle[2]['basic']
                        oc_thr = (basic_1['Close'] - basic_1['Open']) * thresh
                        point1 = basic_1['Open'] - oc_thr
                        point2 = basic_1['Open'] + oc_thr
                        if basic_2['Low'] > basic_0['High'] and basic_2['Open'] >= point1 and \
                                basic_2['Open'] <= point2 and basic_2['Close'] <= basic_1['Close']:
                            return {"type": 'bullish', "style": 'white lines +'}

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            if trading_candle[1]['candlestick']['color'] == 'white':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                if basic_1['High'] < basic_0['Low']:
                    if trading_candle[2]['candlestick']['color'] == 'white':
                        basic_2 = trading_candle[2]['basic']
                        oc_thr = (basic_1['Close'] - basic_1['Open']) * thresh
                        point1 = basic_1['Open'] - oc_thr
                        point2 = basic_1['Open'] + oc_thr
                        if basic_2['High'] < basic_0['Low'] and basic_2['Open'] >= point1 and \
                                basic_2['Open'] <= point2 and basic_2['Close'] <= basic_1['Close']:
                            return {"type": 'bearish', "style": 'white lines -'}

    return None
