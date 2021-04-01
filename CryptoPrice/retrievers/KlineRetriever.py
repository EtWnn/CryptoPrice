from abc import abstractmethod
from typing import Optional

from CryptoPrice.retrievers.AbstractRetriever import AbstractRetriever
from CryptoPrice.storage.KlineDataBase import KlineDataBase
from CryptoPrice.storage.prices import Price
from CryptoPrice.utils.time import TIMEFRAME


class KlineRetriever(AbstractRetriever):

    def __init__(self, name: str, kline_timeframe: TIMEFRAME, closest_window: int = 120):
        super().__init__(name)
        self.db = KlineDataBase(name)
        self.closest_window = closest_window
        self.kline_timeframe = kline_timeframe

    def get_closest_price(self, asset: str, ref_asset: str, timestamp: int) -> Optional[Price]:
        """
        Will get the closest price possible in time for a trading pair asset/ref asset. If no price is found, return
        None.

        Try to fetch a local kline first, if the kline is to far from the wanted timestamp, will fetch a batch of kline
        online and return the closest one

        :param asset: name of the asset in the trading paire (ex 'BTC' in 'BTCUSDT')
        :type asset: str
        :param ref_asset: name of the reference asset in the trading pair (ex 'USDT' in 'BTCUSDT')
        :type ref_asset: str
        :param timestamp: time to fetch the price needed (in seconds)
        :type timestamp: int
        :return: the price closest in time found or None if no price found
        :rtype: Optional[Price]
        """
        # first get closest kline locally
        kline = self.db.get_closest_kline(asset, ref_asset, self.kline_timeframe, timestamp, window=self.closest_window)

        if kline is not None and abs(kline.open_timestamp - timestamp) < self.kline_timeframe.value / 2:
            return Price(kline.open, asset, ref_asset, kline.open_timestamp, kline.source)

        klines = self.get_klines_online(asset, ref_asset, self.kline_timeframe,
                                        timestamp - self.closest_window,
                                        timestamp + self.closest_window)
        self.db.add_klines(klines)

        kline = self.db.get_closest_kline(asset, ref_asset, self.kline_timeframe, timestamp, window=self.closest_window)

        closest_open_timestamp = -1
        if kline is not None:
            closest_open_timestamp = kline.open_timestamp
            # TODO cache result to avoid fetching over and over the API

            return Price(kline.open, asset, ref_asset, kline.open_timestamp, kline.source)

        msg = f"no Kline found for {asset}, {ref_asset}, {self.kline_timeframe}, {timestamp}, w={self.closest_window}"
        self.logger.info(msg)

    @abstractmethod
    def get_klines_online(self, asset: str, ref_asset: str, timeframe: TIMEFRAME, start_time: int, end_time: int):
        """
        Fetch klines online, depends on the retriever used (Binance, Kucoin, CoinAPI...)

        :param asset: asset of the trading pair
        :type asset: str
        :param ref_asset: reference asset of the trading pair
        :type ref_asset: str
        :param timeframe: timeframe for the kline
        :type timeframe: TIMEFRAME
        :param start_time: fetch only klines with an open time greater or equal than start_time
        :type start_time: Optional[int]
        :param end_time: fetch only klines with an open time lower than end_time
        :type end_time: Optional[int]
        :return: list of klines
        :rtype: List[Klines]
        """
        raise NotImplementedError
