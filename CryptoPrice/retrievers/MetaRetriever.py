from typing import List, Optional

from CryptoPrice.common.prices import Price
from CryptoPrice.common.trade import TradingPair
from CryptoPrice.retrievers.AbstractRetriever import AbstractRetriever


class MetaRetriever(AbstractRetriever):

    def __init__(self, retrievers: List[AbstractRetriever]):
        self.retrievers = {r.name: r for r in retrievers}
        super(MetaRetriever, self).__init__("meta_retriever")

    def get_supported_pairs(self) -> List[TradingPair]:
        """
        Return the list of trading pair supported by this retriever

        :return: list of trading pairs
        :rtype: List[TradingPair]
        """
        supported_pairs = []
        for _, retriever in self.retrievers.items():
            supported_pairs.extend(retriever.supported_pairs)
        return supported_pairs

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
        for _, retriever in self.retrievers.items():
            price = retriever.get_closest_price(asset, ref_asset, timestamp)
            if price is not None:
                return price

