import sqlite3
from typing import List, Optional

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
                   end_time: Optional[int] = None):
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
        return self.get_conditions_rows(table, conditions_list=conditions_list)

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

