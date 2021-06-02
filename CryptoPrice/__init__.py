__version__ = "0.1.1"
__author__ = "EtWnn"

from CryptoPrice.retrievers.BinanceRetriever import BinanceRetriever
from CryptoPrice.retrievers.KucoinRetriever import KucoinRetriever
from CryptoPrice.retrievers.CoinbaseRetriever import CoinbaseRetriever
from CryptoPrice.retrievers.MetaRetriever import MetaRetriever


def get_default_retriever() -> MetaRetriever:
    """
    Provides a hands on price retriever made from the default BinanceRetriever, the default KucoinRetriever
    and the default CoinbaseRetriever

    :return: the meta retriever constructed
    :rtype: MetaRetriever
    """
    return MetaRetriever([BinanceRetriever(), KucoinRetriever(), CoinbaseRetriever()])
