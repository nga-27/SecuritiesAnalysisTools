""" three river """
from typing import Union

def unique_three_river(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    """ unique three river """
    # pylint: disable=too-many-nested-blocks
    if not body:
        body = 'body'
    thresh = 0.02
    shadow_ratio = 2.0

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'short' and candle_1['color'] == 'black' and \
                    candle_1['shadow_ratio'] >= shadow_ratio:
                basic_1 = trading_candle[1]['basic']
                basic_0 = trading_candle[0]['basic']
                hi_op = basic_1['High'] - basic_1['Open']
                oc_thr = (basic_1['Open'] - basic_1['Close']) * thresh

                if (hi_op <= oc_thr) and (basic_1['Open'] < basic_0['Open']) and \
                        (basic_1['Low'] < basic_0['Close']):
                    if trading_candle[2]['candlestick']['color'] == 'white':
                        basic_2 = trading_candle[2]['basic']
                        if (basic_2['Open'] >= basic_0['Close']) and \
                                (basic_2['Close'] <= basic_1['Close']):
                            return {"type": 'bullish', "style": '+'}
    return None
