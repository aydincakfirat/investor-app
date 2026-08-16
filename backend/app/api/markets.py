from fastapi import APIRouter, HTTPException, Query

from app.schemas.market import MarketHistory, MarketOverview
from app.services.market_data import (
    MARKET_DEFINITIONS,
    MarketDataError,
    get_market_provider,
)

router = APIRouter(
    prefix="/api/markets",
    tags=["Market Data"],
)


@router.get("/overview", response_model=MarketOverview)
async def get_market_overview():
    provider = get_market_provider()

    quotes = []

    for key in MARKET_DEFINITIONS:
        try:
            quote = await provider.quote(key)
            quotes.append(quote)
        except MarketDataError:
            # One bad symbol should not kill the entire dashboard.
            continue

    return MarketOverview(markets=quotes)


@router.get("/{symbol}/history", response_model=MarketHistory)
async def get_market_history(
    symbol: str,
    interval: str = Query(
        default="1d",
        pattern="^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$",
    ),
    range_: str = Query(
        default="1mo",
        alias="range",
    ),
):
    provider = get_market_provider()

    try:
        candles = await provider.history(
            symbol=symbol,
            interval=interval,
            range_=range_,
        )
    except MarketDataError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return MarketHistory(
        symbol=symbol,
        interval=interval,
        range=range_,
        candles=candles,
    )
