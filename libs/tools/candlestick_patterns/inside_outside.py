from typing import Union

def three_outside(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0['color'] == 'black' and candle_0[body] != 'long':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'long' and candle_1['color'] == 'white':
                basic_1 = trading_candle[1]['basic']
                basic_0 = trading_candle[0]['basic']

                if (basic_0['Low'] > basic_1['Open']) and (basic_0['High'] < basic_1['Close']):
                    if trading_candle[2]['candlestick']['color'] == 'white':
                        basic_2 = trading_candle[2]['basic']
                        if (basic_2['Open'] > basic_1['Open']) and \
                            (basic_2['Open'] < basic_1['Close']) and \
                                (basic_2['Close'] > basic_2['Close']):
                            return {"type": 'bullish', "style": 'up'}

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0['color'] == 'white' and candle_0[body] != 'long':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'long' and candle_1['color'] == 'black':
                basic_1 = trading_candle[1]['basic']
                basic_0 = trading_candle[0]['basic']

                if (basic_0['Low'] > basic_1['Close']) and (basic_0['High'] < basic_1['Open']):
                    if trading_candle[2]['candlestick']['color'] == 'black':
                        basic_2 = trading_candle[2]['basic']
                        if (basic_2['Open'] < basic_1['Open']) and \
                            (basic_2['Open'] > basic_1['Close']) and \
                                (basic_2['Close'] < basic_2['Close']):
                            return {"type": 'bearish', "style": 'down'}
    return None


def three_inside(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'short' and candle_1['color'] == 'white':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']

                if (basic_1['Open'] > basic_0['Close']) and (basic_1['Close'] < basic_0['Open']):
                    if trading_candle[2]['candlestick']['color'] == 'white':
                        basic_2 = trading_candle[2]['basic']
                        if (basic_2['Open'] > basic_1['Open']) and \
                                (basic_2['Open'] < basic_1['Close']):
                            if (basic_2['Close'] > basic_0['Open']):
                                return {"type": 'bullish', "style": 'up'}

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] == 'short' and candle_1['color'] == 'black':
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']

                if (basic_1['Open'] < basic_0['Close']) and (basic_1['Close'] > basic_0['Open']):
                    if trading_candle[2]['candlestick']['color'] == 'black':
                        basic_2 = trading_candle[2]['basic']
                        if (basic_2['Open'] > basic_1['Close']) and \
                                (basic_2['Open'] < basic_1['Open']):
                            if (basic_2['Close'] < basic_0['Open']):
                                return {"type": 'bearish', "style": 'down'}
    return None
