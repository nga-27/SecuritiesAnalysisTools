from typing import Union

def upside_downside_gap_three_methods(trading_candle: list, _: Union[str, None] = None) -> Union[dict, str]:
    if trading_candle[0]['trend'] == 'below':
        if trading_candle[0]['candlestick']['color'] == 'black' and trading_candle[1]['candlestick']['color'] == 'black':
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']
            if basic_1['High'] < basic_0['Low'] and trading_candle[2]['candlestick']['color'] == 'white':
                basic_2 = trading_candle[2]['basic']
                if basic_2['Open'] < basic_1['Open'] and basic_2['Open'] > basic_1['Close'] and \
                        basic_2['Close'] > basic_0['Close'] and basic_2['Close'] < basic_2['Open']:
                    return {"type": 'bearish', "style": 'downside -'}

    if trading_candle[0]['trend'] == 'above':
        if trading_candle[0]['candlestick']['color'] == 'white' and trading_candle[1]['candlestick']['color'] == 'white':
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']
            if basic_1['Low'] > basic_0['High'] and trading_candle[2]['candlestick']['color'] == 'black':
                basic_2 = trading_candle[2]['basic']
                if basic_2['Open'] < basic_1['Close'] and basic_2['Open'] > basic_1['Open'] and \
                        basic_2['Close'] > basic_0['Open'] and basic_2['Close'] < basic_2['Close']:
                    return {"type": 'bullish', "style": 'upside +'}
    return None
