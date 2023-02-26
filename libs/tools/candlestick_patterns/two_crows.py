""" two crows """
from typing import Union

def upside_gap_two_crows(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ upside gap two crows """
    # pylint: disable=too-many-nested-blocks
    if not body:
        body = 'body'

    # Both upside_gap_two_crows and two_crows
    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'short' and candle_1['color'] == 'black':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                if basic_1['Close'] > basic_0['Close']:

                    if trading_candle[1]['candlestick']['color'] == 'black':
                        basic_2 = trading_candle[2]['basic']
                        if (basic_2['Open'] >= basic_1['Open']) and \
                            (basic_2['Close'] <= basic_1['Close']) and \
                                (basic_2['Close'] > basic_0['Close']):
                            return {"type": 'bearish', "style": "upside_gap--"}

                        if (basic_2['Open'] > basic_1['Close']) and \
                            (basic_2['Open'] < basic_1['Open']) and \
                                (basic_2['Close'] < basic_1['Close']) and \
                                (basic_2['Close'] > basic_1['Open']):
                            return {"type": 'bearish', "style": '-'}
    return None
