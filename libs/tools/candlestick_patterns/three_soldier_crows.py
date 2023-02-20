from typing import Union

def three_white_soldiers_black_crows(trading_candle: list,
                                     body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    thresh = 0.3

    if trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0['color'] == 'white' and candle_0[body] != 'short':
            candle_1 = trading_candle[1].get('candlestick')
            if candle_1['color'] == 'white' and candle_1[body] != 'short':
                basic_0 = trading_candle[0].get('basic')
                basic_1 = trading_candle[1].get('basic')
                body_th = ((basic_0.get('Close') - basic_0.get('Open'))
                           * thresh) + basic_0.get('Open')

                if (basic_1.get('Open') > body_th) and (basic_1['Close'] > basic_0['Close']) \
                        and (basic_1['Open'] < basic_0['Close']):
                    candle_2 = trading_candle[2].get('candlestick')
                    if candle_2['color'] == 'white' and candle_2[body] != 'short':
                        basic_2 = trading_candle[2].get('basic')
                        body_th = (
                            (basic_1['Close'] - basic_1['Open']) * thresh) + basic_1['Open']
                        if (basic_2['Open'] > body_th) and (basic_2['Close'] > basic_1['Close']) \
                                and (basic_2['Open'] < basic_1['Close']):
                            return {"type": 'bullish', "style": 'white soldiers'}

    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0['color'] == 'black' and candle_0[body] != 'short':
            candle_1 = trading_candle[1].get('candlestick')
            if candle_1['color'] == 'black' and candle_1[body] != 'short':
                basic_0 = trading_candle[0].get('basic')
                basic_1 = trading_candle[1].get('basic')
                body_th = ((basic_0.get('Close') - basic_0.get('Open'))
                           * (1.0 - thresh)) + basic_0.get('Open')

                if (basic_1.get('Open') < body_th) and (basic_1['Close'] < basic_0['Close']) \
                        and (basic_1['Open'] > basic_0['Close']):
                    candle_2 = trading_candle[2].get('candlestick')
                    if candle_2['color'] == 'black' and candle_2[body] != 'short':
                        basic_2 = trading_candle[2].get('basic')
                        body_th = (
                            (basic_1['Close'] - basic_1['Open']) * (1.0 - thresh)) + basic_1['Open']
                        if (basic_2['Open'] < body_th) and \
                            (basic_2['Close'] < basic_1['Close']) and \
                                (basic_2['Open'] > basic_1['Close']):
                            return {"type": 'bearish', "style": 'black crows'}
    return None
