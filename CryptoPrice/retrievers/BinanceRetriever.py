import traceback
from typing import List

from binance.client import Client
from binance.exceptions import BinanceAPIException

from CryptoPrice.retrievers.KlineRetriever import KlineRetriever
from CryptoPrice.storage.prices import Kline
from CryptoPrice.utils.time import TIMEFRAME


class BinanceRetriever(KlineRetriever):
    """
    docs: https://python-binance.readthedocs.io/en/latest/binance.html
    """

    def __init__(self, kline_timeframe: TIMEFRAME = TIMEFRAME.m1, closest_window: int = 310):
        super(BinanceRetriever, self).__init__('binance', kline_timeframe, closest_window)
        self.client = Client()
        self.kline_traduction = {
            TIMEFRAME.m1: self.client.KLINE_INTERVAL_1MINUTE,
            TIMEFRAME.m3: self.client.KLINE_INTERVAL_3MINUTE,
            TIMEFRAME.m5: self.client.KLINE_INTERVAL_5MINUTE,
            TIMEFRAME.m15: self.client.KLINE_INTERVAL_15MINUTE,
            TIMEFRAME.m30: self.client.KLINE_INTERVAL_30MINUTE,
            TIMEFRAME.h1: self.client.KLINE_INTERVAL_1HOUR,
            TIMEFRAME.h2: self.client.KLINE_INTERVAL_2HOUR,
            TIMEFRAME.h4: self.client.KLINE_INTERVAL_4HOUR,
            TIMEFRAME.h6: self.client.KLINE_INTERVAL_6HOUR,
            TIMEFRAME.h8: self.client.KLINE_INTERVAL_8HOUR,
            TIMEFRAME.h12: self.client.KLINE_INTERVAL_12HOUR,
            TIMEFRAME.d1: self.client.KLINE_INTERVAL_1DAY,
            TIMEFRAME.d3: self.client.KLINE_INTERVAL_3DAY,
            TIMEFRAME.w1: self.client.KLINE_INTERVAL_1WEEK
        }

    def _get_klines_online(self, asset: str, ref_asset: str, timeframe: TIMEFRAME,
                           start_time: int, end_time: int) -> List[Kline]:
        pair_name = asset + ref_asset
        batch_size = 1000
        interval_trad = self.kline_traduction[timeframe]
        try:
            result = self.client.get_klines(symbol=pair_name, interval=interval_trad, startTime=start_time*1000,
                                            endTime=end_time*1000, limit=batch_size)
        except BinanceAPIException as err:
            if err.code == -1121:
                self.logger.warning(f"no {timeframe.name} klines for pair {asset} {ref_asset} between {start_time}"
                                    f" and {end_time}")
            else:
                self.logger.error(str(traceback.format_exc()))
            return []

        klines = []
        for row in result:
            open_timestamp = int(row[0] / 1000)
            open = float(row[1])
            high = float(row[2])
            low = float(row[3])
            close = float(row[4])

            klines.append(Kline(open_timestamp, open, high, low, close,
                                asset, ref_asset, timeframe, source=self.name))

        return klines
