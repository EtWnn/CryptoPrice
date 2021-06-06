from datetime import datetime, timedelta, timezone
import traceback
from typing import List

import cbpro

from CryptoPrice.common.trade import TradingPair
from CryptoPrice.exceptions import RateAPIException
from CryptoPrice.retrievers.KlineRetriever import KlineRetriever
from CryptoPrice.common.prices import Kline
from CryptoPrice.utils.time import TIMEFRAME


class CoinbaseRetriever(KlineRetriever):
    """
    This class is in charge of fetching klines from the Coinbase Pro API

    docs: https://github.com/teleprint-me/coinbasepro-python
    """

    def __init__(self, kline_timeframe: TIMEFRAME = TIMEFRAME.m1, closest_window: int = 310):
        self.client = cbpro.public_client()
        super(CoinbaseRetriever, self).__init__('coinbase', kline_timeframe, closest_window)

    def get_supported_pairs(self) -> List[TradingPair]:
        """
        Return the list of trading pair supported by this retriever

        :return: list of trading pairs
        :rtype: List[TradingPair]
        """
        coinbase_symbols = list(self.client.products.list())
        trading_pairs = [TradingPair(s['base_currency'] + s['quote_currency'],
                                     s['base_currency'],
                                     s['quote_currency'],
                                     source=self.name) for s in coinbase_symbols]
        return trading_pairs

    def _get_klines_online(self, asset: str, ref_asset: str, timeframe: TIMEFRAME,
                           start_time: int, end_time: int) -> List[Kline]:
        """
        Fetch klines online by asking the CoinbasePro API

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
        klines = []
        pair_name = f"{asset}-{ref_asset}"
        granularity = 60 * timeframe.value
        batch_size = 300
        start_datetime = datetime.fromtimestamp(start_time, tz=timezone.utc)
        end_datetime = datetime.fromtimestamp(end_time, tz=timezone.utc)
        while start_datetime < end_datetime:
            batch_end_datetime = start_datetime + timedelta(seconds=granularity*batch_size)
            params = {
                'start': start_datetime.isoformat(),
                'end': batch_end_datetime.isoformat(),
                'granularity': granularity
            }
            result = self.client.products.history(pair_name, params)

            for row in result:
                open_timestamp = int(row[0])
                open = float(row[3])
                high = float(row[2])
                low = float(row[1])
                close = float(row[4])

                klines.append(Kline(open_timestamp, open, high, low, close,
                                    asset, ref_asset, timeframe, source=self.name))

            if len(result):
                start_datetime = datetime.fromtimestamp(result[0][0], tz=timezone.utc) + timedelta(seconds=granularity)
            else:
                start_datetime = start_datetime + timedelta(seconds=granularity * batch_size)

        return klines
