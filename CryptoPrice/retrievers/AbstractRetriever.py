from abc import ABC, abstractmethod
from typing import Optional, List

from CryptoPrice.common.prices import Price
from CryptoPrice.common.trade import TradingPair
from CryptoPrice.utils.LoggerGenerator import LoggerGenerator


class AbstractRetriever(ABC):

    MAX_API_RETRY = 3

    def __init__(self, name: str):
        self.name = name
        self.logger = LoggerGenerator.get_logger(self.name)
        self.supported_pairs = self.get_supported_pairs()

    @abstractmethod
    def get_supported_pairs(self) -> List[TradingPair]:
        """
        Return the list of trading pair supported by this retriever

        :return: list of trading pairs
        :rtype: List[TradingPair]
        """
        raise NotImplementedError

    def get_closest_price(self, asset: str, ref_asset: str, timestamp: int) -> Optional[Price]:
        """
        Will get the closest price possible in time for a trading pair asset/ref asset. If no price is found, return
        None

        :param asset: name of the asset in the trading pair (ex 'BTC' in 'BTCUSDT')
        :type asset: str
        :param ref_asset: name of the reference asset in the trading pair (ex 'USDT' in 'BTCUSDT')
        :type ref_asset: str
        :param timestamp: time to fetch the price needed (in seconds)
        :type timestamp: int
        :return: the price closest in time found or None if no price found
        :rtype: Optional[Price]
        """
        if asset == ref_asset:
            return Price(1, asset, ref_asset, timestamp, source='')
        trading_pair = TradingPair('', asset, ref_asset, '')
        if trading_pair not in self.supported_pairs:
            return
        return self._get_closest_price(asset, ref_asset, timestamp)

    @abstractmethod
    def _get_closest_price(self, asset: str, ref_asset: str, timestamp: int) -> Optional[Price]:
        """
        Will get the closest price possible in time for a trading pair asset/ref asset. If no price is found, return
        None

        :param asset: name of the asset in the trading pair (ex 'BTC' in 'BTCUSDT')
        :type asset: str
        :param ref_asset: name of the reference asset in the trading pair (ex 'USDT' in 'BTCUSDT')
        :type ref_asset: str
        :param timestamp: time to fetch the price needed (in seconds)
        :type timestamp: int
        :return: the price closest in time found or None if no price found
        :rtype: Optional[Price]
        """
        raise NotImplementedError
