from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TradingPair:
    name: str
    asset: str
    ref_asset: str
    source: str

    def __eq__(self, other: TradingPair) -> bool:
        return self.asset == other.asset and self.ref_asset == other.ref_asset
