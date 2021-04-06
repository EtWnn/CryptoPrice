from queue import Queue
from typing import List, Optional, Dict, Tuple

from CryptoPrice.common.prices import Price, MetaPrice
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

    def get_path_price(self, asset: str, ref_asset: str, timestamp: int,
                       preferred_assets: Optional[List[str]] = None, max_depth: int = 3) -> Optional[MetaPrice]:
        """
        Iterator that will get the closest price possible in time for a trading pair asset/ref asset.
        If no price is found, return None

        :param asset: name of the asset in the trading pair (ex 'BTC' in 'BTCUSDT')
        :type asset: str
        :param ref_asset: name of the reference asset in the trading pair (ex 'USDT' in 'BTCUSDT')
        :type ref_asset: str
        :param timestamp: time to fetch the price needed (in seconds)
        :type timestamp: int
        :param preferred_assets: list of assets to construct the price path from. If None, default value is
            ['BTC', 'USDT', 'BUSD', 'ETH']
        :type preferred_assets: Optional[List[str]]
        :param max_depth: maximum number of trading pair to use, default 3
        :type max_depth: int
        :return: the price closest in time found or None if no price found
        :rtype: Optional[MetaPrice]
        """
        if preferred_assets is None:
            preferred_assets = ['BTC', 'ETH']

        assets_neighbours = self.construct_assets_neighbours(preferred_assets + [asset, ref_asset])

        if asset not in assets_neighbours or ref_asset not in assets_neighbours:
            yield None
            return

        seen_assets = [asset]
        current_path = []
        for assets_p, trade_p in self._explore_assets_path(ref_asset, assets_neighbours, seen_assets,
                                                           current_path, max_depth=max_depth):
            yield self.create_meta_price(timestamp, assets_p, trade_p)

    def create_meta_price(self, timestamp: int, seen_assets: List[str],
                          trading_path: List[TradingPair]) -> Optional[MetaPrice]:
        """
        Will try to create a price from a trading path

        :param timestamp: time to fetch the price needed (in seconds)
        :type timestamp: int
        :param seen_assets: list of assets to use (in order)
        :type seen_assets: List[str]
        :param trading_path: list of trading pair to use to follow the path
        :type trading_path: List[TradingPair]
        :return: the meta price associated if possible
        :rtype: Optional[MetaPrice]
        """
        cumulated_price = 1.
        prices = []
        for i, pair in enumerate(trading_path):
            current_asset, next_asset = seen_assets[i:i + 2]
            price = self.retrievers[pair.source].get_closest_price(pair.asset, pair.ref_asset, timestamp)
            if price is None:
                return
            else:
                prices.append(price)
                if price.asset == next_asset:
                    cumulated_price /= price.value
                else:
                    cumulated_price *= price.value
        return MetaPrice(cumulated_price, seen_assets[0], seen_assets[-1], prices)

    def construct_assets_neighbours(self, asset_subsets: List[str]) -> Dict:
        assets_neighbours = {}
        for pair in self.supported_pairs:
            if pair.asset in asset_subsets and pair.ref_asset in asset_subsets:
                try:
                    assets_neighbours[pair.asset][pair.ref_asset].append(pair)
                except KeyError:
                    try:
                        assets_neighbours[pair.asset][pair.ref_asset] = [pair]
                    except KeyError:
                        assets_neighbours[pair.asset] = {pair.ref_asset: [pair]}

                try:
                    assets_neighbours[pair.ref_asset][pair.asset].append(pair)
                except KeyError:
                    try:
                        assets_neighbours[pair.ref_asset][pair.asset] = [pair]
                    except KeyError:
                        assets_neighbours[pair.ref_asset] = {pair.asset: [pair]}
        return assets_neighbours

    @staticmethod
    def _explore_assets_path(target_asset: str, assets_neighbours: Dict,
                             seen_assets: List[str], current_path: List[TradingPair],
                             max_depth: int = 3) -> Tuple[List[str], List[TradingPair]]:
        """
        Iterator that will explore the trading possibilities to link one asset to another one through a trading path

        :param target_asset: asset to look for
        :type target_asset: str
        :param assets_neighbours: dictionary of neighbours for assets
        :type assets_neighbours: Dict
        :param seen_assets: assets already seen on the path
        :type seen_assets: List[str]
        :param current_path: trading pair to use (in order) to follow the path to the target asset
        :type current_path: List[TradingPair]
        :param max_depth: maximum number of trading pair to use, default 3
        :type max_depth: int
        :return: list of assets to explore and the trading path to take
        :rtype: Tuple[List[str], List[TradingPair]]
        """
        to_explore = Queue()
        to_explore.put((seen_assets, current_path))
        while to_explore.qsize():
            seen_assets, current_path = to_explore.get()
            current_asset = seen_assets[-1]
            for next_asset in assets_neighbours[current_asset]:
                if next_asset not in seen_assets:
                    for pair in assets_neighbours[current_asset][next_asset]:
                        if next_asset == target_asset:
                            yield seen_assets + [next_asset], current_path + [pair]
                        elif len(current_path) + 1 < max_depth:
                            to_explore.put((seen_assets + [next_asset], current_path + [pair]))
