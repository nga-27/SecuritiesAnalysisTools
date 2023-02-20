from typing import Union

def homing_pigeon(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] != 'long' and candle_1['color'] == 'black':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                if (basic_1['Open'] < basic_0['Open']) and (basic_1['Close'] > basic_0['Close']):
                    return {"type": 'bullish', "style": '+'}
    return None
