===============================
Welcome to CryptoPrice 0.1.1dev
===============================


Note
----

This library is under development by EtWnn, feel free to drop your suggestions or remarks in
the discussion tab of the git repo. You are also welcome to contribute by submitting PRs.

This library is made to retrieve price or candle history of crypto assets using multiple sources.

**Source Code:**
    https://github.com/EtWnn/CryptoPrice
**Documentation:**
    https://cryptoprice.readthedocs.io


Features
--------

The idea is to have under a single library several price history API to be able to fetch effortlessly the price of large
amount of different tokens or to compare the price difference between exchanges.

It currently includes:
    - Binance API
    - Kucoin API
    - Cross-API logic

Quick Tour
----------

**Installation**

``CryptoPrice`` is available on `PYPI <https://pypi.org/project/python-CryptoPrice/>`_, install with ``pip``:

.. code:: bash

    pip install python-CryptoPrice

You can also install the latest developments (not stable):

.. code:: bash

    pip install git+https://github.com/EtWnn/CryptoPrice.git@develop


**Examples**

A price retriever is already provided by the library, but feel free to check the
`documentation <https://cryptoprice.readthedocs.io>`_ to instantiate one yourself.

.. code-block:: python

    import datetime
    from CryptoPrice import get_default_retriever

    retriever = get_default_retriever()

    asset = 'BTC'
    ref_asset = 'USDT'
    timestamp = int(datetime.datetime(2021, 1, 1, 15, 14).timestamp())

    # will return the first price price found close to the timestamp
    retriever.get_closest_price(asset, ref_asset, timestamp)

.. code-block:: bash

    >>Price(value=29480.0, asset='BTC', ref_asset='USDT', timestamp=1609510440, source='binance')

You can also fetch a price even if the trading pair does not exist: The retriever (MetaRetriever) will find a path with
several trading pairs to estimate the price between the asset and the ref asset. This method takes much more time
than the one above as several API calls (or database requests) have to be made.

.. code-block:: python

    import datetime
    from CryptoPrice import get_default_retriever

    retriever = get_default_retriever()

    asset = 'LTC'
    ref_asset = 'XRP'
    timestamp = int(datetime.datetime(2021, 3, 3, 15, 14).timestamp())

    # will return an average price of several trading path
    price = retriever.get_mean_price(asset, ref_asset, timestamp)
    if price is not None:  # price found
        print(f"{asset} = {price.value:.5f} {ref_asset}, source: {price.source}")

.. code-block:: bash

    >>LTC = 420.80573 XRP, source: {'kucoin', 'binance'}


Donation
--------


If this library has helped you in any way, feel free to donate:

- **BTC**: 14ou4fMYoMVYbWEKnhADPJUNVytWQWx9HG
- **ETH**: 0xfb0ebcf8224ce561bfb06a56c3b9a43e1a4d1be2
- **LTC**: LfHgc969RFUjnmyLn41SRDvmT146jUg9tE
- **EGLD**: erd1qk98xm2hgztvmq6s4jwtk06g6laattewp6vh20z393drzy5zzfrq0gaefh