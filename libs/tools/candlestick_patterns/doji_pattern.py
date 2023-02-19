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