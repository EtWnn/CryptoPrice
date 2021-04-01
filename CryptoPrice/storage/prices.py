from dataclasses import dataclass

from CryptoPrice.utils.time import TIMEFRAME


@dataclass
class Price:
    value: float
    asset: str
    ref_asset: str
    timestamp: int
    source: str


@dataclass
class Kline:
    open: float
    high: float
    low: float
    close: float
    asset: str
    ref_asset: str
    open_timestamp: int
    timeframe: TIMEFRAME
    source: str
