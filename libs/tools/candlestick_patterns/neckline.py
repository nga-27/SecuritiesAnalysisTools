from typing import Union

def on_in_neck_line(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    thresh = 0.05
    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            if trading_candle[1]['candlestick']['color'] == 'white':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                if basic_1['Open'] < basic_0['Low']:
                    oc_thr = (basic_0['Open'] - basic_0['Close']) * thresh
                    point1 = basic_0['Close'] - oc_thr
                    point2 = basic_0['Close'] + oc_thr
                    if basic_1['Close'] >= point1 and basic_1['Close'] <= point2:
                        return {"type": 'bearish', "style": 'in -'}
                    if basic_1['Close'] <= basic_0['Close'] and basic_1['Close'] >= basic_0['Low']:
                        return {"type": 'bearish', "style": 'on -'}

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            if trading_candle[1]['candlestick']['color'] == 'black':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                if basic_1['Open'] > basic_0['High']:
                    oc_thr = (basic_0['Close'] - basic_0['Open']) * thresh
                    point1 = basic_0['Close'] - oc_thr
                    point2 = basic_0['Close'] + oc_thr
                    if basic_1['Close'] >= point1 and basic_1['Close'] <= point2:
                        return {"type": 'bullish', "style": 'in +'}
                    if basic_1['Close'] >= basic_0['Close'] and basic_1['Close'] <= basic_0['High']:
                        return {"type": 'bullish', "style": 'on +'}
    return None
