import time
from abc import abstractmethod
from typing import Optional, List

from CryptoPrice.exceptions import RateAPIException
from CryptoPrice.retrievers.AbstractRetriever import AbstractRetriever
from CryptoPrice.storage.KlineDataBase import KlineDataBase
from CryptoPrice.storage.prices import Price, Kline
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

        if kline is not None:
            if abs(kline.open_timestamp - timestamp) < self.kline_timeframe.value * 60 / 2:
                return Price(kline.open, asset, ref_asset, kline.open_timestamp, kline.source)
            else:
                msg = f"{timestamp} and {kline.open_timestamp} are to far apart for {self.kline_timeframe.name}," \
                      f" fetching online"
                self.logger.debug(msg)
        else:
            msg = f"no kline in around time {timestamp} with a {self.closest_window} window, fetching online"
            self.logger.debug(msg)

        klines = self.get_klines_online(asset, ref_asset, self.kline_timeframe,
                                        timestamp - self.closest_window,
                                        timestamp + self.closest_window)
        self.db.add_klines(klines, ignore_if_exists=True)

        kline = self.db.get_closest_kline(asset, ref_asset, self.kline_timeframe, timestamp, window=self.closest_window)

        closest_open_timestamp = -1
        if kline is not None:
            closest_open_timestamp = kline.open_timestamp
            # TODO cache result to avoid fetching over and over the API

            return Price(kline.open, asset, ref_asset, kline.open_timestamp, kline.source)

        msg = f"no Kline found for {asset}, {ref_asset}, {self.kline_timeframe.name}, {timestamp}," \
              f" w={self.closest_window}"

        self.logger.debug(msg)

    def get_klines_online(self, asset: str, ref_asset: str, timeframe: TIMEFRAME, start_time: int, end_time: int,
                          retry_count: int = 0) -> List[Kline]:
        """
        This method handles RateAPIException and calls _get_klines_online which will effectively
        retrieve the online data

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
        :param retry_count: internal use, number of recursive loops done on this method
        :type retry_count: int
        :return: list of klines
        :rtype: List[Kline]
        """
        if retry_count > AbstractRetriever.MAX_API_RETRY:
            raise RuntimeError(f"The API rate limits has been breached {retry_count} times in a row")
        try:
            return self._get_klines_online(asset, ref_asset, timeframe, start_time, end_time)
        except RateAPIException as err:
            time.sleep(err.retry_after)
            return self._get_klines_online(asset, ref_asset, timeframe, start_time, end_time)

    @abstractmethod
    def _get_klines_online(self, asset: str, ref_asset: str, timeframe: TIMEFRAME, start_time: int,
                           end_time: int) -> List[Kline]:
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
        :rtype: List[Kline]
        """
        raise NotImplementedError
