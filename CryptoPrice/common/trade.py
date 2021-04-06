from dataclasses import dataclass


@dataclass
class TradingPair:
    name: str
    asset: str
    ref_asset: str
    source: str
