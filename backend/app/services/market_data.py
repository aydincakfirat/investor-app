from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

import httpx

from app.core.config import get_settings
from app.schemas.market import MarketCandle, MarketQuote


class MarketDataError(Exception):
    pass


class MarketDataProvider(ABC):
    @abstractmethod
    async def quote(self, key: str) -> MarketQuote:
        raise NotImplementedError

    @abstractmethod
    async def history(
        self,
        symbol: str,
        interval: str = "1d",
        range_: str = "1mo",
    ) -> list[MarketCandle]:
        raise NotImplementedError


class YahooFinanceProvider(MarketDataProvider):
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

    def __init__(self) -> None:
        self.timeout = 10.0

    async def _request_chart(
        self,
        symbol: str,
        *,
        interval: str = "1d",
        range_: str = "1d",
    ) -> dict:
        url = f"{self.BASE_URL}/{symbol}"

        params = {
            "interval": interval,
            "range": range_,
        }

        headers = {
            "User-Agent": "investment-intelligence-platform/1.0",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=headers,
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise MarketDataError(
                f"Yahoo Finance request failed for {symbol}: {exc}"
            ) from exc

        data = response.json()

        chart = data.get("chart", {})
        error = chart.get("error")

        if error:
            raise MarketDataError(
                f"Yahoo Finance error for {symbol}: {error}"
            )

        results = chart.get("result")

        if not results:
            raise MarketDataError(
                f"No Yahoo Finance data returned for {symbol}"
            )

        return results[0]

    async def quote(self, key: str) -> MarketQuote:
        definition = MARKET_DEFINITIONS.get(key)

        if definition is None:
            raise MarketDataError(f"Unknown market key: {key}")

        result = await self._request_chart(
            definition["symbol"],
            interval="1d",
            range_="5d",
        )

        meta = result.get("meta", {})

        # ── Current price ────────────────────────────────────────────────
        price = meta.get("regularMarketPrice")

        # ── Historical closes ────────────────────────────────────────────
        indicators = result.get("indicators", {})
        quote_data = indicators.get("quote", [{}])[0]

        closes = [
            value
            for value in quote_data.get("close", [])
            if value is not None
        ]

        # Some instruments don't provide regularMarketPrice.
        # In that case use the latest valid close.
        if price is None and closes:
            price = closes[-1]

        # ── Previous close ───────────────────────────────────────────────
        previous_close = meta.get("previousClose")

        # Yahoo doesn't always return previousClose.
        # If missing, use the close immediately before the latest close.
        if previous_close is None and len(closes) >= 2:
            previous_close = closes[-2]

        # ── Change calculation ───────────────────────────────────────────
        change = None
        change_percent = None

        if price is not None and previous_close is not None:
            change = price - previous_close

            if previous_close != 0:
                change_percent = (
                    change / previous_close
                ) * 100

        # ── Timestamp ────────────────────────────────────────────────────
        timestamp = None

        market_timestamp = meta.get("regularMarketTime")

        if market_timestamp:
            timestamp = datetime.fromtimestamp(
                market_timestamp,
                tz=timezone.utc,
            )

        return MarketQuote(
            key=key,
            name=definition["name"],
            symbol=definition["symbol"],
            region=definition["region"],
            price=price,
            currency=meta.get("currency"),
            change=change,
            change_percent=change_percent,
            timestamp=timestamp,
        )

    async def history(
        self,
        symbol: str,
        interval: str = "1d",
        range_: str = "1mo",
    ) -> list[MarketCandle]:

        result = await self._request_chart(
            symbol,
            interval=interval,
            range_=range_,
        )

        timestamps = result.get("timestamp", [])

        quote_data = result.get("indicators", {}).get(
            "quote",
            [{}],
        )[0]

        opens = quote_data.get("open", [])
        highs = quote_data.get("high", [])
        lows = quote_data.get("low", [])
        closes = quote_data.get("close", [])
        volumes = quote_data.get("volume", [])

        candles: list[MarketCandle] = []

        for i, timestamp in enumerate(timestamps):
            candles.append(
                MarketCandle(
                    timestamp=datetime.fromtimestamp(
                        timestamp,
                        tz=timezone.utc,
                    ),
                    open=opens[i] if i < len(opens) else None,
                    high=highs[i] if i < len(highs) else None,
                    low=lows[i] if i < len(lows) else None,
                    close=closes[i] if i < len(closes) else None,
                    volume=volumes[i] if i < len(volumes) else None,
                )
            )

        return candles


# ── Market definitions ────────────────────────────────────────────────────────

MARKET_DEFINITIONS = {
    # Turkey
    "bist100": {
        "name": "BIST 100",
        "symbol": "XU100.IS",
        "region": "Turkey",
    },
    "bist_banks": {
        "name": "BIST Banks",
        "symbol": "XBANK.IS",
        "region": "Turkey",
    },
    "usd_try": {
        "name": "USD/TRY",
        "symbol": "TRY=X",
        "region": "Turkey",
    },
    "eur_try": {
        "name": "EUR/TRY",
        "symbol": "EURTRY=X",
        "region": "Turkey",
    },
    "gold": {
        "name": "Gold",
        "symbol": "GC=F",
        "region": "Turkey",
    },
    "brent": {
        "name": "Brent",
        "symbol": "BZ=F",
        "region": "Turkey",
    },
    "tr10y": {
        "name": "TR 10Y",
        "symbol": "^TR10Y",
        "region": "Turkey",
    },

    # United States
    "sp500": {
        "name": "S&P 500",
        "symbol": "^GSPC",
        "region": "United States",
    },
    "nasdaq100": {
        "name": "Nasdaq 100",
        "symbol": "^NDX",
        "region": "United States",
    },
    "dowjones": {
        "name": "Dow Jones",
        "symbol": "^DJI",
        "region": "United States",
    },
    "vix": {
        "name": "VIX",
        "symbol": "^VIX",
        "region": "United States",
    },
    "us10y": {
        "name": "US 10Y",
        "symbol": "^TNX",
        "region": "United States",
    },
    "dxy": {
        "name": "DXY",
        "symbol": "DX-Y.NYB",
        "region": "United States",
    },

    # Europe
    "dax": {
        "name": "DAX",
        "symbol": "^GDAXI",
        "region": "Europe",
    },
    "cac40": {
        "name": "CAC 40",
        "symbol": "^FCHI",
        "region": "Europe",
    },
    "ftse100": {
        "name": "FTSE 100",
        "symbol": "^FTSE",
        "region": "Europe",
    },
    "eurostoxx50": {
        "name": "Euro Stoxx 50",
        "symbol": "^STOXX50E",
        "region": "Europe",
    },
    "eurusd": {
        "name": "EUR/USD",
        "symbol": "EURUSD=X",
        "region": "Europe",
    },
}


# ── Mock provider ─────────────────────────────────────────────────────────────

class MockMarketDataProvider(MarketDataProvider):
    async def quote(self, key: str) -> MarketQuote:
        definition = MARKET_DEFINITIONS[key]

        return MarketQuote(
            key=key,
            name=definition["name"],
            symbol=definition["symbol"],
            region=definition["region"],
            price=100.0,
            currency="USD",
            change=1.0,
            change_percent=1.0,
            timestamp=datetime.now(timezone.utc),
        )

    async def history(
        self,
        symbol: str,
        interval: str = "1d",
        range_: str = "1mo",
    ) -> list[MarketCandle]:
        return []


# ── Provider factory ──────────────────────────────────────────────────────────

def get_market_provider() -> MarketDataProvider:
    settings = get_settings()

    if settings.market_data_provider.lower() == "yahoo":
        return YahooFinanceProvider()

    return MockMarketDataProvider()
