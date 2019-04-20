def calculate_rsi(data):
    avggain = 0
    avgloss = 0
    for i in range(0, len(data)-1):
        diff = data[i]["close"] - data[i+1]["close"]
        if diff < 0:
            avgloss += diff*(-1)
        elif diff > 0:
            avggain += diff
    avggain /= 14.0
    avgloss /= 14.0
    rsi = 0
    if avgloss != 0:
        rsi = 100 - 100 / (1 + (avggain/avgloss))
    return rsi


def calculate_k_r(data, c):
    H_14 = max([row["high"] for row in data])
    L_14 = min([row["low"] for row in data])
    K = 0
    R = 0
    if (H_14 - L_14) != 0:
        K = 100*((c - L_14)/(H_14 - L_14))
        R = -100*((H_14 - c)/(H_14 - L_14))
    return K, R


def calculate_proc(data, period, c):
    proc = 0
    if data[period-1]["close"] != 0:
        proc = (c - data[period - 1]["close"]) / data[period-1]["close"]
    return proc


def calculate_obv(features, history, c, volume, trading_window):
    obv = features[trading_window-1][8]
    if c > history[trading_window-1]["close"]:
        obv = obv + volume
    elif c < history[trading_window-1]["close"]:
        obv = obv - volume
    return obv


def ema(n, prev_ema, x):
    weight = 2.0/(n + 1.0)
    ema = (x - prev_ema) * weight + prev_ema
    return ema


def fmacd(features, c):
    ema_12 = ema(12, features[0][10], c)
    ema_26 = ema(26, features[0][11], c)
    return ema_12, ema_26, (ema_12 - ema_26)
