"""Persist market quotes returned by a market data provider."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import MarketAsset, MarketQuoteCache
from app.schemas.market import MarketQuote


async def persist_quote(session: AsyncSession, quote: MarketQuote) -> None:
    """Create or update an asset and append its latest quote to the cache."""
    result = await session.execute(
        select(MarketAsset).where(MarketAsset.key == quote.key)
    )
    asset = result.scalar_one_or_none()

    if asset is None:
        asset = MarketAsset(
            key=quote.key,
            name=quote.name,
            symbol=quote.symbol,
            region=quote.region,
            currency=quote.currency,
            created_at=datetime.now(timezone.utc),
        )
        session.add(asset)
        await session.flush()
    else:
        asset.name = quote.name
        asset.symbol = quote.symbol
        asset.region = quote.region
        asset.currency = quote.currency

    timestamp = quote.timestamp or datetime.now(timezone.utc)
    cached_quote = MarketQuoteCache(
        asset_id=asset.id,
        price=quote.price,
        change=quote.change,
        change_percent=quote.change_percent,
        timestamp=timestamp,
    )
    session.add(cached_quote)


async def persist_quotes(
    session: AsyncSession,
    quotes: list[MarketQuote],
) -> None:
    """Persist a batch of quotes atomically."""
    for quote in quotes:
        await persist_quote(session, quote)
    await session.commit()
