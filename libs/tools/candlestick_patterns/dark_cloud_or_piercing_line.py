from typing import Union

def dark_cloud_or_piercing_line(trading_candle: list,
                                body: Union[str, None] = None) -> Union[dict, None]:
    # Dark Cloud
    if not body:
        body = 'body'
    if trading_candle[0].get('trend') == 'above':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0.get(body) == 'long':
            if candle_0.get('color') == 'white':
                basic_0 = trading_candle[0].get('basic')
                high_0 = basic_0.get('High')
                basic_1 = trading_candle[1].get('basic')
                open_1 = basic_1.get('Open')
                if open_1 > high_0:
                    close_1 = basic_1.get('Close')
                    close_0 = basic_0.get('Close')
                    open_0 = basic_0.get('Open')
                    mid_pt = ((close_0 - open_0) / 2.0) + open_0
                    if close_1 <= mid_pt:
                        return {'type': 'bearish', 'style': 'darkcloud'}

    # Piercing Line
    elif trading_candle[0].get('trend') == 'below':
        candle_0 = trading_candle[0].get('candlestick')
        if candle_0.get(body) == 'long':
            if candle_0.get('color') == 'black':
                basic_0 = trading_candle[0].get('basic')
                low_0 = basic_0.get('Low')
                basic_1 = trading_candle[1].get('basic')
                open_1 = basic_1.get('Open')
                if open_1 < low_0:
                    close_1 = basic_1.get('Close')
                    close_0 = basic_0.get('Close')
                    open_0 = basic_0.get('Open')
                    mid_pt = ((close_0 - open_0) / 2.0) + open_0
                    if close_1 >= mid_pt:
                        return {'type': 'bullish', 'style': 'piercing line'}

    return None