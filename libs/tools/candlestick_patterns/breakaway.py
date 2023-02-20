""" breakaway """
from typing import Union

def breakaway(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ breakaway """
    # pylint: disable=too-many-nested-blocks,too-many-branches
    if not body:
        body = 'body'

    if trading_candle[0]['trend'] == 'below':
        if trading_candle[0]['candlestick'][body] == 'long' and \
            trading_candle[0]['candlestick']['color'] == 'black':
            if trading_candle[0]['basic']['Low'] > trading_candle[1]['basic']['High']:
                candle_1 = trading_candle[1]['candlestick']

                if candle_1[body] == 'short' and candle_1['color'] == 'black':
                    basic_2 = trading_candle[2]['basic']
                    basic_1 = trading_candle[1]['basic']
                    if (basic_2['Close'] < basic_1['Open']) and (basic_2['Open'] < basic_1['Open']):
                        if basic_2['Low'] < basic_1['Low']:
                            candle_3 = trading_candle[3]['candlestick']

                            if candle_3[body] == 'short' and candle_3['color'] == 'black':
                                if trading_candle[3]['basic']['Low'] < basic_2['Low']:
                                    candle_4 = trading_candle[4]['candlestick']
                                    if candle_4[body] == 'long' and candle_4['color'] == 'white':
                                        basic_4 = trading_candle[4]['basic']
                                        if basic_4['Close'] > basic_1['Open'] and \
                                            basic_4['Close'] <= trading_candle[0]['basic']['Close']:
                                            return {"type": 'bullish', "style": 'breakaway +'}

    if trading_candle[0]['trend'] == 'above':
        if trading_candle[0]['candlestick'][body] == 'long' and \
            trading_candle[0]['candlestick']['color'] == 'white':
            if trading_candle[0]['basic']['High'] < trading_candle[1]['basic']['Low']:
                candle_1 = trading_candle[1]['candlestick']

                if candle_1[body] == 'short' and candle_1['color'] == 'white':
                    basic_2 = trading_candle[2]['basic']
                    basic_1 = trading_candle[1]['basic']
                    if (basic_2['Close'] > basic_1['Open']) and (basic_2['Open'] > basic_1['Open']):
                        if basic_2['High'] > basic_1['High']:
                            candle_3 = trading_candle[3]['candlestick']

                            if candle_3[body] == 'short' and candle_3['color'] == 'white':
                                if trading_candle[3]['basic']['High'] > basic_2['High']:
                                    candle_4 = trading_candle[4]['candlestick']
                                    if candle_4[body] == 'long' and candle_4['color'] == 'black':
                                        basic_4 = trading_candle[4]['basic']
                                        if basic_4['Close'] < basic_1['Open'] and \
                                            basic_4['Close'] >= trading_candle[0]['basic']['Close']:
                                            return {"type": 'bearish', "style": 'breakaway -'}
    return None
