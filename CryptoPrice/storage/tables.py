from typing import List, Optional

from CryptoPrice.utils.time import TIMEFRAME


class Table:
    """
    This class represent a table of a database
    @DynamicAttrs
    """

    def __init__(self, name: str, columns_names: List[str], columns_sql_types: List[str],
                 primary_key: Optional[str] = None, primary_key_sql_type: Optional[str] = None):
        self.name = name
        self.columns_names = columns_names
        self.columns_sql_types = columns_sql_types
        self.primary_key = primary_key
        self.primary_key_sql_type = primary_key_sql_type

        for column_name in self.columns_names:
            try:
                value = getattr(self, column_name)
                raise ValueError(f"the name {column_name} conflicts with an existing attribute of value {value}")
            except AttributeError:
                setattr(self, column_name, column_name)

        if self.primary_key is not None:
            setattr(self, self.primary_key, self.primary_key)


class KlineTable(Table):
    def __init__(self, asset: str, ref_asset: str, timeframe: TIMEFRAME):
        name = f"{asset}_{ref_asset}_{timeframe.name}"
        super().__init__(name,
                         [
                             "open",
                             "high",
                             "low",
                             "close"
                         ],
                         [
                             "REAL",
                             "REAL",
                             "REAL",
                             "REAL"
                         ],
                         primary_key="open_timestamp",
                         primary_key_sql_type="INTEGER"
                         )


class KlineCacheTable(Table):

    def __init__(self, asset: str, ref_asset: str, timeframe: TIMEFRAME):
        name = f"{asset}_{ref_asset}_{timeframe.name}_cache"
        super().__init__(name,
                         [
                             "closest",
                             "window"
                         ],
                         [
                             "INTEGER",
                             "INTEGER"
                         ],
                         primary_key="timestamp",
                         primary_key_sql_type="INTEGER"
                         )
