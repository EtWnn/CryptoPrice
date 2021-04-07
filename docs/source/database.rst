DataBase
==========

To avoid spamming APIs and to save time, this library save locally the price data retrieved.


Tables
--------

.. automodule:: CryptoPrice.storage.tables
    :special-members: __init__
    :members:
    :undoc-members:

DataBase
--------

This class is the base of all database, it contains the main logic to communicate with a sqlite db.

.. automodule:: CryptoPrice.storage.DataBase
    :special-members: __init__
    :members:
    :undoc-members:

KlineDataBase
-------------

This is a child class of DataBase, specifi for candle data (ohlc).

.. automodule:: CryptoPrice.storage.KlineDataBase
    :special-members: __init__
    :members:
    :undoc-members: