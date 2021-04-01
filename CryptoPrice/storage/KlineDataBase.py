import sqlite3
from typing import List, Optional, Tuple

from CryptoPrice.storage.DataBase import DataBase, SQLConditionEnum
from CryptoPrice.storage.prices import Kline
from CryptoPrice.storage.tables import KlineTable
from CryptoPrice.utils.time import TIMEFRAME


class KlineDataBase(DataBase):

    def __init__(self, name: str):
        super().__init__(name)

    def add_klines(self, klines: List[Kline], ignore_if_exists: bool = False):
        """
        add several klines to the database

        :param klines: list of klines to add to the database
        :type klines: List[Kline]
        :param ignore_if_exists: if integrity errors should be ignored, default False
        :type ignore_if_exists: bool
        :return: None
        :rtype: None
        """
        for kline in klines:
            table = KlineTable(klines[0].asset, kline.ref_asset, kline.timeframe)
            row = (kline.open_timestamp, kline.open, kline.high, kline.low, kline.close)
            try:
                self.add_row(table, row, auto_commit=False)
            except sqlite3.IntegrityError as err:
                if not ignore_if_exists:
                    raise err
        self.commit()

    def get_klines(self, asset: str, ref_asset: str, timeframe: TIMEFRAME, start_time: Optional[int] = None,
                   end_time: Optional[int] = None) -> List[Kline]:
        """
        return the klines corresponding to a trading pair and a timeframe
        a time window can also be provided.

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
        table = KlineTable(asset, ref_asset, timeframe)
        conditions_list = []
        if start_time is not None:
            conditions_list.append((table.open_timestamp,
                                    SQLConditionEnum.greater_equal,
                                    start_time))
        if end_time is not None:
            conditions_list.append((table.open_timestamp,
                                    SQLConditionEnum.lower,
                                    end_time))
        rows = self.get_conditions_rows(table, conditions_list=conditions_list)
        return [self.row_to_kline(asset, ref_asset, timeframe, r) for r in rows]

    def get_closest_kline(self, asset: str, ref_asset: str, timeframe: TIMEFRAME, timestamp: int,
                          window: int = 120) -> Optional[Kline]:
        """
        Return the closest Kline in a time window for a trading pair and a timeframe.
        If there is no Kline, None is returned

        :param asset: asset of the trading pair
        :type asset: str
        :param ref_asset: reference asset of the trading pair
        :type ref_asset: str
        :param timeframe: timeframe for the kline
        :type timeframe: TIMEFRAME
        :param timestamp: time of interest in seconds
        :type timestamp: int
        :param window: time window in seconds for the kline to look
        :type window: int
        :return: the Kline with an open time the closest to the provided timestamp
        :rtype: Optional[Kline]
        """
        table = KlineTable(asset, ref_asset, timeframe)
        conditions_list = [
            (table.open_timestamp,
             SQLConditionEnum.greater_equal,
             timestamp - window),
            (table.open_timestamp,
             SQLConditionEnum.lower,
             timestamp + window)
        ]
        order_list = [f'ABS({table.open_timestamp} - {timestamp})']
        klines = self.get_conditions_rows(table, conditions_list=conditions_list, order_list=order_list)
        if len(klines):
            return self.row_to_kline(asset, ref_asset, timeframe, klines[0])

    def drop_pair_table(self, asset: str, ref_asset: str, timeframe: TIMEFRAME):
        """
        drop the table associated with a trading pair and a time frame

        :param asset: asset of the trading pair
        :type asset: str
        :param ref_asset: reference asset of the trading pair
        :type ref_asset: str
        :param timeframe: timeframe for the kline
        :type timeframe: TIMEFRAME
        :return: None
        :rtype: None
        """
        table = KlineTable(asset, ref_asset, timeframe)
        super().drop_table(table)

    def row_to_kline(self, asset: str, ref_asset: str, timeframe: TIMEFRAME, row: Tuple):
        """
        Take a row from the KlineDatabase and transform it into a Kline object

        :param asset: asset of the trading pair
        :type asset: str
        :param ref_asset: reference asset of the trading pair
        :type ref_asset: str
        :param timeframe: timeframe for the kline
        :type timeframe: TIMEFRAME
        :param row: raw data from the database
        :type row: Tuple
        :return: the Kline corresponding to the args
        :rtype: Kline
        """
        return Kline(*row, asset=asset, ref_asset=ref_asset, timeframe=timeframe, source=self.name)

