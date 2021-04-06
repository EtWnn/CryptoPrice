from dataclasses import dataclass
from typing import List

from CryptoPrice.utils.time import TIMEFRAME


@dataclass
class Price:
    value: float
    asset: str
    ref_asset: str
    timestamp: int
    source: str


@dataclass
class MetaPrice:
    value: float
    asset: str
    ref_asset: str
    prices: List[Price]


@dataclass
class Kline:
    open_timestamp: int
    open: float
    high: float
    low: float
    close: float
    asset: str
    ref_asset: str
    timeframe: TIMEFRAME
    source: str
