from queue import Queue
from typing import List, Optional, Dict, Tuple, Iterator

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

    def get_mean_price(self, asset: str, ref_asset: str, timestamp: int, preferred_assets: Optional[List[str]] = None,
                       max_depth: int = 3, max_depth_range: int = 0) -> Optional[MetaPrice]:
        """
        Will use the method get_path_prices and return the mean price of an asset compared to a reference asset
        on a given timestamp.

        :param asset: name of the asset to get the price of
        :type asset: str
        :param ref_asset: name of the reference asset
        :type ref_asset: str
        :param timestamp: time to fetch the price needed (in seconds)
        :type timestamp: int
        :param preferred_assets: list of assets to construct the price path from. If None, default value is
            ['BTC', 'ETH']
        :type preferred_assets: Optional[List[str]]
        :param max_depth: maximum number of trading pair to use, default 3
        :type max_depth: int
        :param max_depth_range: maximum length difference between different trading path. If the first trading path has
            a length of 1 and this parameter is equal to 2, trading_path with a length superior to 3 will be ignored
        :type max_depth_range: int
        :return: Metaprice reflecting the value calculated with a mean of trading path
        :rtype: Optional[MetaPrice]
        """
        meta_prices = []
        min_depth = max_depth + 1
        for meta_price in self.get_path_prices(asset, ref_asset, timestamp, preferred_assets,
                                               max_depth, -1):
            if meta_price is not None:
                if min_depth > max_depth:
                    min_depth = len(meta_price.prices)
                if len(meta_price.prices) - min_depth > max_depth_range:
                    break
                else:
                    meta_prices.append(meta_price)
        if len(meta_prices):
            return MetaPrice.mean_from_meta_price(meta_prices)

    def get_path_prices(self, asset: str, ref_asset: str, timestamp: int,
                        preferred_assets: Optional[List[str]] = None, max_depth: int = 2,
                        max_depth_range: int = -1) -> Iterator[MetaPrice]:
        """
        Iterator that return MetaPrices that estimates the price of an asset compared to a reference asset.
        It will use the trading pair at its disposal to create trading path from the asset to the ref asset.
        It use a BFS algorithm, so the shortest path will be returned first.
        If no price is found, return None

        :param max_depth_range:
        :type max_depth_range:
        :param asset: name of the asset to get the price of
        :type asset: str
        :param ref_asset: name of the reference asset
        :type ref_asset: str
        :param timestamp: time to fetch the price needed (in seconds)
        :type timestamp: int
        :param preferred_assets: list of assets to construct the price path from. If None, default value is
            ['BTC', 'ETH']
        :type preferred_assets: Optional[List[str]]
        :param max_depth: maximum number of trading pair to use, default 2
        :type max_depth: int
        :param max_depth_range: maximum length difference between different trading path. If the first trading path has
            a length of 1 and this parameter is equal to 2, trading_path with a length superior to 3 will be ignored.
            Default -1 means that this parameter is ignored.
        :type max_depth_range: int
        :return: Metaprice reflecting the value calculated through a trading path
        :rtype: Optional[MetaPrice]
        """
        if asset == ref_asset:
            yield MetaPrice(1, asset, ref_asset, [], source=set('',))
            return
        if preferred_assets is None:
            preferred_assets = ['BTC', 'ETH']

        assets_neighbours = self.construct_assets_neighbours(preferred_assets + [asset, ref_asset])

        if asset not in assets_neighbours or ref_asset not in assets_neighbours:
            yield None
            return

        seen_assets = [asset]
        current_path = []
        for assets_p, trade_p in self._explore_assets_path(ref_asset, assets_neighbours, seen_assets,
                                                           current_path, max_depth=max_depth,
                                                           max_depth_range=max_depth_range):
            price_path = []
            for pair in trade_p:
                price = self.retrievers[pair.source].get_closest_price(pair.asset, pair.ref_asset, timestamp)
                if price is not None:
                    price_path.append(price)
                else:
                    break
            if len(price_path) + 1 == len(assets_p):  # all prices have been found
                yield MetaPrice.from_price_path(assets_p, price_path)

    def construct_assets_neighbours(self, asset_subsets: List[str]) -> Dict:
        """
        Construct a dictionary of neighbours assets, with the trading pairs needed to get from one asset to another

        :param asset_subsets: list of assets to use among supported assets
        :type asset_subsets: List[str]
        :return: assets_neighbours
        :rtype: Dict
        """
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
                             seen_assets: List[str], current_path: List[TradingPair], max_depth: int = 3,
                             max_depth_range: int = -1) -> Iterator[Tuple[List[str], List[TradingPair]]]:
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
        :param max_depth_range: maximum length difference between different trading path. If the first trading path has
            a length of 1 and this parameter is equal to 2, trading_path with a length superior to 3 will be ignored.
            Default -1 means that this parameter is ignored.
        :type max_depth_range: int
        :return: list of assets to explore and the trading path to take
        :rtype: Tuple[List[str], List[TradingPair]]
        """
        to_explore = Queue()
        to_explore.put((seen_assets, current_path))
        min_depth = None
        while to_explore.qsize():
            seen_assets, current_path = to_explore.get()
            current_asset = seen_assets[-1]
            if min_depth is not None and len(current_path) + 1 - min_depth > max_depth_range:
                break

            for next_asset in assets_neighbours[current_asset]:

                if next_asset not in seen_assets:

                    for pair in assets_neighbours[current_asset][next_asset]:
                        if next_asset == target_asset:
                            if min_depth is None and max_depth_range >= 0:
                                min_depth = len(current_path) + 1
                            yield seen_assets + [next_asset], current_path + [pair]

                        elif len(current_path) + 1 < max_depth:
                            to_explore.put((seen_assets + [next_asset], current_path + [pair]))
