from typing import Union

def matching_high_low(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    thresh = 0.03

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            if trading_candle[1]['candlestick']['color'] == 'black':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                point1 = ((basic_0['Open'] - basic_0['Close']) * thresh) + basic_0['Close']
                point2 = basic_0['Close'] - \
                    ((basic_0['Open'] - basic_0['Close']) * thresh)
                if (basic_1['Open'] < basic_0['Open']) and (basic_1['Close'] <= point1) and \
                        (basic_1['Close'] >= point2):
                    return {"type": 'bullish', "style": 'low'}

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            if trading_candle[1]['candlestick']['color'] == 'white':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                point1 = ((basic_0['Close'] - basic_0['Open']) * thresh) + basic_0['Close']
                point2 = basic_0['Close'] - \
                    ((basic_0['Close'] - basic_0['Open']) * thresh)
                if (basic_1['Open'] > basic_0['Open']) and (basic_1['Close'] <= point1) and \
                        (basic_1['Close'] >= point2):
                    return {"type": 'bearish', "style": 'high'}
    return None
