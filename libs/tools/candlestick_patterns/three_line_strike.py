""" three line strike """
from typing import Union

def three_line_strike(trading_candle: list, _: Union[str, None] = None) -> Union[dict, None]:
    """ three line strike """
    # pylint: disable=too-many-nested-blocks
    if trading_candle[0]['trend'] == 'below':
        if trading_candle[0]['candlestick']['color'] == 'black' and \
            trading_candle[1]['candlestick']['color'] == 'black' \
                and trading_candle[2]['candlestick']['color'] == 'black':
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']

            if basic_1['Open'] < basic_0['Open'] and basic_1['Close'] < basic_0['Close']:
                basic_2 = trading_candle[2]['basic']
                if basic_2['Open'] < basic_1['Open'] and basic_2['Close'] < basic_1['Close']:
                    if trading_candle[3]['candlestick']['color'] == 'white':
                        basic_3 = trading_candle[3]['basic']
                        if basic_3['Open'] <= basic_2['Close'] and \
                                basic_3['Close'] >= basic_0['Open']:
                            return {"type": 'bearish', "style": '-'}

    if trading_candle[0]['trend'] == 'above':
        if trading_candle[0]['candlestick']['color'] == 'white' and \
            trading_candle[1]['candlestick']['color'] == 'white' \
                and trading_candle[2]['candlestick']['color'] == 'white':
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']

            if basic_1['Open'] > basic_0['Open'] and basic_1['Close'] > basic_0['Close']:
                basic_2 = trading_candle[2]['basic']
                if basic_2['Open'] > basic_1['Open'] and basic_2['Close'] > basic_1['Close']:
                    if trading_candle[3]['candlestick']['color'] == 'black':
                        basic_3 = trading_candle[3]['basic']
                        if basic_3['Open'] >= basic_2['Close'] and \
                                basic_3['Close'] <= basic_0['Open']:
                            return {"type": 'bullish', "style": '+'}
    return None
