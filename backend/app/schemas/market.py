from datetime import datetime

from pydantic import BaseModel


class MarketQuote(BaseModel):
    key: str
    name: str
    symbol: str
    region: str
    price: float | None
    currency: str | None
    change: float | None
    change_percent: float | None
    timestamp: datetime | None


class MarketOverview(BaseModel):
    markets: list[MarketQuote]


class MarketCandle(BaseModel):
    timestamp: datetime
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: int | None


class MarketHistory(BaseModel):
    symbol: str
    interval: str
    range: str
    candles: list[MarketCandle]
