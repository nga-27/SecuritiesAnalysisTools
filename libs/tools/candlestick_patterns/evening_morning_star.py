from typing import Union

def evening_morning_star(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    # Evening star
    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            basic_0 = trading_candle[0].get('basic')
            basic_1 = trading_candle[1].get('basic')
            close_0 = basic_0.get('Close')
            open_1 = basic_1.get('Open')

            if open_1 > close_0:
                candle_1 = trading_candle[1].get('candlestick')
                if candle_1[body] == 'short':
                    close_1 = basic_1.get('Close')
                    if close_1 > close_0:
                        basic_2 = trading_candle[2].get('basic')
                        open_2 = basic_2.get('Open')

                        if open_2 < min(close_1, open_1):
                            open_0 = basic_0.get('Open')
                            mid_pt = ((close_0 - open_0) / 2.0) + open_0
                            close_2 = basic_2.get('Close')
                            if close_2 <= mid_pt:
                                if candle_1['doji']:
                                    if basic_1['Low'] > max(basic_0['High'], basic_1['High']):
                                        return {"type": 'bearish', "style": 'abandoned baby -'}
                                    return {"type": 'bearish', "style": 'evening star DOJI'}
                                return {'type': 'bearish', 'style': 'evening star'}

    # Morning star
    if trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            basic_0 = trading_candle[0].get('basic')
            basic_1 = trading_candle[1].get('basic')
            close_0 = basic_0.get('Close')
            open_1 = basic_1.get('Open')

            if open_1 < close_0:
                candle_1 = trading_candle[1].get('candlestick')
                if candle_1[body] == 'short':
                    close_1 = basic_1.get('Close')
                    if close_1 < close_0:
                        basic_2 = trading_candle[2].get('basic')
                        open_2 = basic_2.get('Open')

                        if open_2 > max(close_1, open_1):
                            open_0 = basic_0.get('Open')
                            mid_pt = ((close_0 - open_0) / 2.0) + open_0
                            close_2 = basic_2.get('Close')
                            if close_2 >= mid_pt:
                                if candle_1['doji']:
                                    if basic_1['High'] < min(basic_0['Low'], basic_1['Low']):
                                        return {"type": 'bullish', "style": 'abandoned baby +'}
                                    return {"type": 'bullish', "style": 'morning star: DOJI'}
                                return {'type': 'bullish', 'style': 'morning star'}
    return None
