from __future__ import annotations
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

    @staticmethod
    def from_price_path(assets: List[str], price_path: List[Price]) -> MetaPrice:
        """
        Construct a MetaPrice instance from a price path

        :param assets: list of assets seen on the path (in order)
        :type assets: List[str]
        :param price_path: list of price used to go from the first asset to the last one
        :type price_path: List[Price]
        :return: the MetaPrice representing the price between the first and the last asset
        :rtype: MetaPrice
        """
        if len(assets) < 2:
            raise ValueError(f"at least two assets are required, {len(assets)} were received")
        if len(assets) != len(price_path) + 1:
            raise ValueError(f"the number of assets and prices are not coherent")
        cumulated_price = 1.
        for i, price in enumerate(price_path):
            current_asset, next_asset = assets[i:i + 2]
            if price.asset == next_asset:
                cumulated_price /= price.value
            else:
                cumulated_price *= price.value
        return MetaPrice(cumulated_price, assets[0], assets[-1], price_path)


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
