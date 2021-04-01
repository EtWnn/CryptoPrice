from enum import IntEnum


class TIMEFRAME(IntEnum):
    """
    Enumeration for kline time frame.
    m : minutes
    h: hours
    d: days
    w: weeks
    The value of an enumeration member is the number of minutes in the time frame
    """
    m1 = 1
    m3 = 3
    m5 = 5
    m15 = 15
    m30 = 30
    h1 = 60
    h2 = 120
    h4 = 240
    h6 = 360
    h8 = 480
    h12 = 720
    d1 = 1440
    d3 = 4320
    w1 = 10080
