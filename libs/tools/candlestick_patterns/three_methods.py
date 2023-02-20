from typing import Union

def upside_downside_gap_three_methods(trading_candle: list, _: Union[str, None] = None) -> Union[dict, str]:
    if trading_candle[0]['trend'] == 'below':
        if trading_candle[0]['candlestick']['color'] == 'black' and trading_candle[1]['candlestick']['color'] == 'black':
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']
            if basic_1['High'] < basic_0['Low'] and trading_candle[2]['candlestick']['color'] == 'white':
                basic_2 = trading_candle[2]['basic']
                if basic_2['Open'] < basic_1['Open'] and basic_2['Open'] > basic_1['Close'] and \
                        basic_2['Close'] > basic_0['Close'] and basic_2['Close'] < basic_2['Open']:
                    return {"type": 'bearish', "style": 'downside -'}

    if trading_candle[0]['trend'] == 'above':
        if trading_candle[0]['candlestick']['color'] == 'white' and trading_candle[1]['candlestick']['color'] == 'white':
            basic_0 = trading_candle[0]['basic']
            basic_1 = trading_candle[1]['basic']
            if basic_1['Low'] > basic_0['High'] and trading_candle[2]['candlestick']['color'] == 'black':
                basic_2 = trading_candle[2]['basic']
                if basic_2['Open'] < basic_1['Close'] and basic_2['Open'] > basic_1['Open'] and \
                        basic_2['Close'] > basic_0['Open'] and basic_2['Close'] < basic_2['Close']:
                    return {"type": 'bullish', "style": 'upside +'}
    return None


def rising_falling_three_methods(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'

    # Rising three methods (continuation of bull trend)
    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            basic_0 = trading_candle[0].get('basic')
            high_0 = basic_0.get('High')
            low_0 = basic_0.get('Low')
            close_0 = basic_0.get('Close')
            basic_1 = trading_candle[1].get('basic')

            if high_0 >= max(basic_1.get('Open'), basic_1.get('Close')):
                if low_0 <= min(basic_1.get('Open'), basic_1.get('Close')):
                    if trading_candle[1]['candlestick'][body] == 'short':
                        basic_2 = trading_candle[1].get('basic')

                        if high_0 >= max(basic_2.get('Open'), basic_2.get('Close')):
                            if low_0 <= min(basic_2.get('Open'), basic_2.get('Close')):
                                basic_3 = trading_candle[1].get('basic')
                                if high_0 >= max(basic_3.get('Open'), basic_3.get('Close')):
                                    if low_0 <= min(basic_3.get('Open'), basic_3.get('Close')):
                                        candle_4 = trading_candle[4].get('candlestick')
                                        if candle_4[body] == 'long' and \
                                                candle_4['color'] == 'white':
                                            if trading_candle[4].get('basic', {}).get('Close') \
                                                > close_0:
                                                return {"type": 'bullish',
                                                        "style": 'rising three methods'}

    # Falling three methods (continuation of bear trend)
    if trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            basic_0 = trading_candle[0].get('basic')
            high_0 = basic_0.get('High')
            low_0 = basic_0.get('Low')
            close_0 = basic_0.get('Close')
            basic_1 = trading_candle[1].get('basic')

            if low_0 <= min(basic_1.get('Open'), basic_1.get('Close')):
                if high_0 >= max(basic_1.get('Open'), basic_1.get('Close')):
                    if trading_candle[1]['candlestick'][body] == 'short':
                        basic_2 = trading_candle[1].get('basic')
                        if low_0 <= min(basic_2.get('Open'), basic_2.get('Close')):

                            if high_0 >= max(basic_2.get('Open'), basic_2.get('Close')):
                                basic_3 = trading_candle[1].get('basic')
                                if low_0 <= min(basic_3.get('Open'), basic_3.get('Close')):
                                    if high_0 >= max(basic_3.get('Open'), basic_3.get('Close')):
                                        candle_4 = trading_candle[4].get('candlestick')
                                        if candle_4[body] == 'long' and \
                                                candle_4['color'] == 'black':
                                            if trading_candle[4].get('basic', {}).get('Close') \
                                                < close_0:
                                                return {"type": 'bearish',
                                                        "style": 'falling three methods'}
    return None
