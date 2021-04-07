__version__ = "0.1.0dev"
__author__ = "EtWnn"

from CryptoPrice.retrievers.BinanceRetriever import BinanceRetriever
from CryptoPrice.retrievers.KucoinRetriever import KucoinRetriever
from CryptoPrice.retrievers.MetaRetriever import MetaRetriever

retriever = MetaRetriever([BinanceRetriever(), KucoinRetriever()])
