from abc import ABC, abstractmethod
from typing import Optional

from CryptoPrice.storage.prices import Price
from CryptoPrice.utils.LoggerGenerator import LoggerGenerator


class AbstractRetriever(ABC):

    def __init__(self, name: str):
        self.name = name
        self.logger = LoggerGenerator.get_logger(self.name)

    @abstractmethod
    def get_closest_price(self, asset: str, ref_asset: str, timestamp: int) -> Optional[Price]:
        """
        Will get the closest price possible in time for a trading pair asset/ref asset. If no price is found, return
        None

        :param asset: name of the asset in the trading paire (ex 'BTC' in 'BTCUSDT')
        :type asset: str
        :param ref_asset: name of the reference asset in the trading pair (ex 'USDT' in 'BTCUSDT')
        :type ref_asset: str
        :param timestamp: time to fetch the price needed (in seconds)
        :type timestamp: int
        :return: the price closest in time found or None if no price found
        :rtype: Optional[Price]
        """
        raise NotImplementedError
