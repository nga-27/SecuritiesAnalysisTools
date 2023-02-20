""" tri star """
from typing import Union

def tri_star(trading_candle: list, _: Union[str, None] = None) -> Union[dict, None]:
    """ tri star """
    if trading_candle[0]['trend'] == 'below':
        if trading_candle[0]['candlestick']['doji'] and \
            trading_candle[1]['candlestick']['doji'] and \
                trading_candle[2]['candlestick']['doji']:
            if trading_candle[1]['basic']['Close'] < trading_candle[0]['basic']['Close']:
                if trading_candle[1]['basic']['Close'] < trading_candle[2]['basic']['Close']:
                    return {"type": 'bullish', "style": 'tri star +'}

    if trading_candle[0]['trend'] == 'above':
        if trading_candle[0]['candlestick']['doji'] and \
            trading_candle[1]['candlestick']['doji'] and \
                trading_candle[2]['candlestick']['doji']:
            if trading_candle[1]['basic']['Close'] > trading_candle[0]['basic']['Close']:
                if trading_candle[1]['basic']['Close'] > trading_candle[2]['basic']['Close']:
                    return {"type": 'bearish', "style": 'tri star -'}
    return None
