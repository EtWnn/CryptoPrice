import traceback
from typing import List

from kucoin.client import Market

from CryptoPrice.retrievers.KlineRetriever import KlineRetriever
from CryptoPrice.storage.prices import Kline
from CryptoPrice.utils.time import TIMEFRAME


class KucoinRetriever(KlineRetriever):
    """
    docs: https://github.com/Kucoin/kucoin-python-sdk
    https://docs.kucoin.com
    """

    def __init__(self, kline_timeframe: TIMEFRAME = TIMEFRAME.m1, closest_window: int = 310):
        super(KucoinRetriever, self).__init__('kucoin', kline_timeframe, closest_window)
        self.client = Market(url='https://api.kucoin.com')
        self.kline_traduction = {
            TIMEFRAME.m1: '1min',
            TIMEFRAME.m3: '3min',
            TIMEFRAME.m5: '5min',
            TIMEFRAME.m15: '15min',
            TIMEFRAME.m30: '30min',
            TIMEFRAME.h1: '1hour',
            TIMEFRAME.h2: '2hour',
            TIMEFRAME.h4: '4hour',
            TIMEFRAME.h6: '6hour',
            TIMEFRAME.h8: '8hour',
            TIMEFRAME.h12: '12hour',
            TIMEFRAME.d1: '1day',
            TIMEFRAME.w1: '1week'
        }

    def get_klines_online(self, asset: str, ref_asset: str, timeframe: TIMEFRAME,
                          start_time: int, end_time: int) -> List[Kline]:
        pair_name = f"{asset}-{ref_asset}"
        batch_size = 1500
        interval_trad = self.kline_traduction[timeframe]
        result = self.client.get_kline(symbol=pair_name, kline_type=interval_trad, startAt=start_time,
                                       endAt=end_time, pageSize=batch_size)

        klines = []
        for row in result:
            open_timestamp = int(row[0])
            open = float(row[1])
            close = float(row[2])
            high = float(row[3])
            low = float(row[4])

            klines.append(Kline(open_timestamp, open, high, low, close,
                                asset, ref_asset, timeframe, source=self.name))

        return klines
