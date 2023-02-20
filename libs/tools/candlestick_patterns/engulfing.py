from typing import Union

def engulfing(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    if trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0.get('color') == 'black':
            candle_1 = trading_candle[1].get('candlestick')
            if candle_1[body] == 'long' and candle_1['color'] == 'white':
                basic_0 = trading_candle[0].get('basic')
                basic_1 = trading_candle[1].get('basic')
                if basic_0.get('High') <= basic_1.get('Close'):
                    if basic_0.get('Low') >= basic_1.get('Open'):
                        return {"type": 'bullish', "style": '+'}

    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0.get('color') == 'white':
            candle_1 = trading_candle[1].get('candlestick')
            if candle_1[body] == 'long' and candle_1['color'] == 'black':
                basic_0 = trading_candle[0].get('basic')
                basic_1 = trading_candle[1].get('basic')
                if basic_0.get('High') <= basic_1.get('Open'):
                    if basic_0.get('Low') >= basic_1.get('Close'):
                        return {"type": 'bearish', "style": '-'}
    return None
