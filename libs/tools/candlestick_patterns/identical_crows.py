from typing import Union

def identical_three_crows(trading_candle: list, body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    thresh = 0.03
    size_range = 0.05

    if trading_candle[0]['trend'] == 'above':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] != 'short' and candle_0['color'] == 'black':
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] != 'short' and candle_1['color'] == 'black':
                basic_1 = trading_candle[1]['basic']
                basic_0 = trading_candle[0]['basic']
                point1 = ((basic_0['Open'] - basic_0['Close']) * thresh) + basic_0['Close']
                point2 = basic_0['Close'] - \
                    ((basic_0['Open'] - basic_0['Close']) * thresh)
                if (basic_1['Open'] <= point1) and (basic_1['Close'] >= point2):
                    candle_2 = trading_candle[2]['candlestick']
                    if candle_2[body] != 'short' and candle_2['color'] == 'black':
                        basic_2 = trading_candle[2]['basic']
                        point1 = (
                            (basic_1['Open'] - basic_1['Close']) * thresh) + basic_1['Close']
                        point2 = basic_1['Close'] - \
                            ((basic_1['Open'] - basic_1['Close']) * thresh)
                        if (basic_2['Open'] <= point1) and (basic_2['Open'] >= point2):
                            length_0 = basic_0['Open'] - basic_0['Close']
                            upper_th = length_0 * (1.0 + size_range)
                            lower_th = length_0 * (1.0 - size_range)
                            length_1 = basic_1['Open'] - basic_1['Close']
                            length_2 = basic_2['Open'] - basic_2['Close']
                            if (length_1 <= upper_th) and (length_1 >= lower_th):
                                if (length_2 <= upper_th) and (length_2 >= lower_th):
                                    return {"type": 'bearish', "style": '-'}
    return None
