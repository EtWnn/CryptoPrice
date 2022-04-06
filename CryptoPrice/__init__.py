from CryptoPrice.__about__ import *

from CryptoPrice.retrievers.BinanceRetriever import BinanceRetriever
from CryptoPrice.retrievers.KucoinRetriever import KucoinRetriever
from CryptoPrice.retrievers.MetaRetriever import MetaRetriever


def get_default_retriever() -> MetaRetriever:
    """
    Provides a hands on price retriever made from the default BinanceRetriever and the default KucoinRetriever


    :return: the meta retriever constructed
    :rtype: MetaRetriever
    """
    return MetaRetriever([BinanceRetriever(), KucoinRetriever()])
