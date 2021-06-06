import sqlite3
from typing import List, Optional, Tuple

from CryptoPrice.storage.DataBase import DataBase, SQLConditionEnum
from CryptoPrice.common.prices import Kline
from CryptoPrice.storage.tables import KlineTable, KlineCacheTable
from CryptoPrice.utils.time import TIMEFRAME


class KlineDataBase(DataBase):

    def __init__(self, name: str):
        """
        Instantiate a kline database object, the name will be used for the saving file

        :param name: name of the database
        :type name: str
        """
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

    def get_cache_closest(self, asset: str, ref_asset: str, timeframe: TIMEFRAME,
                          timestamp: int) -> Tuple[Optional[int], int]:
        """
        Look if a request for the timestamp has been saved in the cache
        Return the cached timestamp of the previously selected kline along with the window used at that time
        a timestamp of -1 means that no result were found

        :param asset: asset of the trading pair
        :type asset: str
        :param ref_asset: reference asset of the trading pair
        :type ref_asset: str
        :param timeframe: timeframe for the kline
        :type timeframe: TIMEFRAME
        :param timestamp: request timestamp
        :type timestamp: int
        :return: cached_timestamp, window
        :rtype: Optional[int], int
        """

        table = KlineCacheTable(asset, ref_asset, timeframe)
        row = self.get_row_by_key(table, timestamp)
        if row is not None:
            return row[1:]
        else:
            return None, -1

    def add_cache_closest(self, asset: str, ref_asset: str, timeframe: TIMEFRAME, timestamp: int,
                          closest_timestamp: int, window: int):
        """
        Save the result of a previous closest price request

        :param asset: asset of the trading pair
        :type asset: str
        :param ref_asset: reference asset of the trading pair
        :type ref_asset: str
        :param timeframe: timeframe for the kline
        :type timeframe: TIMEFRAME
        :param timestamp: request timestamp
        :type timestamp: int
        :param closest_timestamp: the timestamp that got selected as the closest
        :type closest_timestamp: int
        :param window: time window in seconds that got used to fetch the klines
        :type window: int
        :return: None
        :rtype: None
        """
        table = KlineCacheTable(asset, ref_asset, timeframe)
        row = (timestamp, closest_timestamp, window)
        self.add_row(table, row, update_if_exists=True)

    def drop_cache_tables(self):
        """
        Delete all the cache tables stored in the database

        :return: None
        :rtype: None
        """
        tables = [t[1] for t in self.get_tables_descriptions()]
        tables = [table for table in tables if table.endswith('_cache')]
        self.drop_tables(tables)

