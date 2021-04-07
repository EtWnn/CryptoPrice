Getting Started
===============

Installation
------------

``CryptoPrice`` is available on `PYPI <https://pypi.org/project/python-CryptoPrice/>`_, install with ``pip``:

.. code:: bash

    pip install python-CryptoPrice

You can also install the latest developments (not stable):

.. code:: bash

    pip install git+https://github.com/EtWnn/CryptoPrice.git@develop

APIs
-----

This library only use public API endpoints, so there is no need to register to any API.


Get a retriever
---------------

To fetch some prices, you will need to use a retriever, there are several retrievers in this library
but one is already instantiated for you:

.. code:: python

    from CryptoPrice import retriever

You can also refer to the :doc:`retrievers` to learn how to instantiate your custom retriever.


Examples
--------

Here are some examples, with the retriever instantiated in the library

.. code-block:: python

    import datetime
    from CryptoPrice import retriever

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
    from CryptoPrice import retriever

    asset = 'LTC'
    ref_asset = 'XRP'
    timestamp = int(datetime.datetime(2021, 3, 3, 15, 14).timestamp())

    # will return an average price of several trading path
    price = retriever.get_mean_price(asset, ref_asset, timestamp)
    if price is not None:  # price found
        print(f"{asset} = {price.value:.5f} {ref_asset}, source: {price.source}")

.. code-block:: bash

    >>LTC = 420.80573 XRP, source: mean_meta