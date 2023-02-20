""" advanced block """
from typing import Union

def advance_block(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ advance block """
    if not body:
        body = 'body'

    if trading_candle[0]['trend'] == 'above':
        if trading_candle[0]['candlestick']['color'] == 'white':
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']
            if basic_1['Open'] > basic_0['Open'] and basic_1['Open'] < basic_0['Close'] and \
                    basic_1['Close'] > basic_0['Close'] and \
                        trading_candle[1]['candlestick']['color'] == 'white':
                candle_2 = trading_candle[2]['candlestick']
                if candle_2[body] == 'short' and candle_2['color'] == 'white':
                    basic_2 = trading_candle[2]['basic']
                    if basic_2['Open'] > basic_1['Open'] and \
                        basic_2['Open'] < basic_1['Close'] and \
                            basic_2['Close'] > basic_1['Close']:
                        return {"type": 'bearish', "style": '-'}
    return None
