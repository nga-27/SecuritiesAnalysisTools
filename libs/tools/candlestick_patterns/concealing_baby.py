from typing import Union

def concealing_baby_swallow(trading_candle: list,
                            body: Union[str, None] = None) -> Union[dict, None]:
    if not body:
        body = 'body'
    mf_shadow_ratio = 1.03
    shadow_ratio = 1.6
    thresh = 0.02

    if trading_candle[0]['trend'] == 'below':
        candle_0 = trading_candle[0]['candlestick']
        if candle_0[body] != 'short' and candle_0['color'] == 'black' and \
                candle_0['shadow_ratio'] <= mf_shadow_ratio:
            candle_1 = trading_candle[1]['candlestick']
            if candle_1[body] != 'short' and candle_1['color'] == 'black' and \
                    candle_1['shadow_ratio'] <= mf_shadow_ratio:
                basic_0 = trading_candle[0]['basic']
                basic_1 = trading_candle[1]['basic']
                mid_pt = ((basic_0['Open'] - basic_0['Close'])
                          * 0.5) + basic_0['Close']
                if (basic_1['Open'] < mid_pt) and (basic_1['Open'] >= basic_0['Close']):
                    candle_2 = trading_candle[2]['candlestick']
                    if candle_2[body] == 'short' and candle_2['color'] == 'black' and \
                            candle_2['shadow_ratio'] >= shadow_ratio:
                        basic_2 = trading_candle[2]['basic']
                        oc_thr = (basic_2['Open'] - basic_2['Close']) * thresh
                        cl_low = (basic_2['Close'] - basic_2['Low'])
                        if (cl_low <= oc_thr) and (basic_2['Open'] < basic_1['Close']) and \
                                (basic_2['High'] >= basic_1['Close']):
                            candle_3 = trading_candle[3]['candlestick']
                            if candle_3['color'] == 'black' and \
                                candle_3[body] != 'short' and \
                                    candle_3['shadow_ratio'] <= mf_shadow_ratio:
                                basic_3 = trading_candle[3]['basic']
                                if (basic_3['Close'] <= basic_2['Close']) and \
                                        (basic_3['Open'] > basic_2['Open']):
                                    return {"type": 'bullish', "style": 'swallow +'}
    return None
