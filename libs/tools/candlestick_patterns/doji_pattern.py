from typing import Union

def doji_pattern(trading_candle: list, _: Union[str, None] = None) -> Union[dict, None]:
    THRESH = 0.05
    day_candle = trading_candle[0]
    if day_candle.get('candlestick', {}).get('doji'):
        close = day_candle['basic']['Close']
        high = day_candle['basic']['Close']
        low = day_candle['basic']['Low']

        clo_low = close - low
        hi_low = high - low
        if clo_low >= ((1.0 - THRESH) * hi_low):
            return {'type': 'bullish', 'style': 'dragonfly'}
        if clo_low <= (THRESH * hi_low):
            return {'type': 'bearish', 'style': 'gravestone'}
    return None


def doji_star(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    if trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0['color'] == 'black' and candle_0[body] != 'short':
            basic_1 = trading_candle[1].get('basic')
            basic_0 = trading_candle[0].get('basic')
            if basic_1.get('High') <= basic_0.get('Close'):
                candle_1 = trading_candle[1].get('candlestick')
                if candle_1.get('doji'):
                    return {"type": 'bullish', "style": "+"}

    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0['color'] == 'white' and candle_0[body] != 'short':
            basic_1 = trading_candle[1].get('basic')
            basic_0 = trading_candle[0].get('basic')
            if basic_1.get('Low') >= basic_0.get('Close'):
                candle_1 = trading_candle[1].get('candlestick')
                if candle_1.get('doji'):
                    return {"type": 'bearish', "style": "-"}
    return None
