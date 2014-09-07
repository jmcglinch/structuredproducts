import math

def black_scholes_model(days, underlying_price, 
        striking_price, v, r):
    t = float(days)/float(365)
    d1 = float(math.log(float(underlying_price)/float(striking_price)) \
        + (r + v * float(v)/float(2)) * t)/\
        float(v * math.sqrt(t))
    d2 = d1 - (v * math.sqrt(t))
    y = float(1) / float(1 + .2316419 * math.fabs(d1))
    z = float(.3989423)*math.exp(-float(d1**2)/float(2))
    x = 1 - z*(1.330274*y**5 - \
                1.821256*y**4 + \
                1.781478*y**3 - \
                .356538*y**2 + \
                .3193815*y)
    if d1 < 0: 
        nd1 = float(1) - x
    else:
        nd1 = x
    y = float(1) / float(1 + .2316419 * math.fabs(d2))
    z = float(.3989423)*math.exp(-float(d2**2)/float(2))
    x = 1 - z*(1.330274*y**5 - \
                1.821256*y**4 + \
                1.781478*y**3 - \
                .356538*y**2 + \
                .3193815*y)
    if d2 < 0:
        nd2 = float(1) - x
    else:
        nd2 = x
    value = float(underlying_price*nd1) - \
        float(striking_price)*math.exp(-r*t) * nd2
    return round(value,4)

def implied_volatility(days, underlying_price, striking_price, 
        v, r, target_val, incr):
    while True:
        val = black_scholes_model(days, underlying_price, 
            striking_price, v, r)
        if round(val, 2) == round(target_val, 2):
            return v
            break
        elif round(val,2) == underlying_price:
            return None
            break
        else:
            v += incr