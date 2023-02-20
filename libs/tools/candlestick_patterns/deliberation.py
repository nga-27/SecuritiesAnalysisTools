""" deliberation """
from typing import Union

def deliberation(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ deliberation """
    if not body:
        body = 'body'

    # pylint: disable=too-many-nested-blocks
    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'long' and candle_0['color'] == 'white':
                basic_0 = trading_candle[0]['basic']
                mid_pt = (basic_0['Close'] - basic_0['Open']) * 0.5
                basic_1 = trading_candle[1]['basic']
                if (basic_1['Open'] > mid_pt) and (basic_1['Open'] < basic_0['Close']) and \
                        (basic_1['Close'] > basic_0['Close']):
                    candle_2 = trading_candle[2]['candlestick']
                    if candle_2[body] == 'short' or candle_2['color'] == 'white':
                        basic_2 = trading_candle[2]['basic']
                        if basic_2['Open'] > basic_1['Close']:
                            return {"type": 'bearish', "style": '-'}
    return None
