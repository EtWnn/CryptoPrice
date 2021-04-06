from dataclasses import dataclass


@dataclass
class TradingPair:
    asset: str
    ref_asset: str
