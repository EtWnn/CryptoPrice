Retrievers
==========

The retrievers handles the communication between an API, the user and a database. With each user's request, it will try
to search the response in a local database and if necessary will ask an API.


AbstractRetriever
-----------------

This class is the base of all retrievers, it contains the main logic.

.. automodule:: CryptoPrice.retrievers.AbstractRetriever
    :special-members: __init__
    :members:
    :undoc-members:

KlineRetriever
--------------

This class is specific for the retriever linked to an API with candle (ohlc) data, it implements the KlineDataBase for
this kind of data.

.. automodule:: CryptoPrice.retrievers.KlineRetriever
    :special-members: __init__
    :members:
    :undoc-members:

Implemented Retrievers
-----------------------

Below are the retrievers implemented in this library.

.. automodule:: CryptoPrice.retrievers.BinanceRetriever
    :special-members: __init__
    :members:
    :undoc-members:

.. automodule:: CryptoPrice.retrievers.KucoinRetriever
    :special-members: __init__
    :members:
    :undoc-members:

MetaRetriever
-------------

This retriever is made above several specified retrievers. It allows to create price data
across different exchanges / APIs.

.. automodule:: CryptoPrice.retrievers.MetaRetriever
    :special-members: __init__
    :members:
    :undoc-members:


