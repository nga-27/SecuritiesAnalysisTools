from typing import Union

def tasuki_gap_upside_downside(trading_candle: list,
                               body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            if trading_candle[1]['candlestick']['color'] == 'white':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                if basic_1['Low'] > basic_0['High']:
                    if trading_candle[2]['candlestick']['color'] == 'black':
                        basic_2 = trading_candle[2]['basic']
                        if basic_2['Open'] <= basic_1['Close'] and \
                                basic_2['Open'] >= basic_1['Open']:
                            if basic_2['Close'] < basic_1['Open'] and \
                                    basic_2['Close'] > basic_0['Close']:
                                return {"type": 'bullish', "style": 'upside +'}

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            if trading_candle[1]['candlestick']['color'] == 'black':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                if basic_0['Low'] > basic_1['High']:
                    if trading_candle[2]['candlestick']['color'] == 'white':
                        basic_2 = trading_candle[2]['basic']
                        if basic_2['Open'] <= basic_1['Open'] and \
                                basic_2['Open'] >= basic_1['Close']:
                            if basic_2['Close'] > basic_1['Open'] and \
                                    basic_2['Close'] < basic_0['Close']:
                                return {"type": 'bearish', "style": 'downside -'}
    return None
