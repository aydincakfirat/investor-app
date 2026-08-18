from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models.market import MarketAsset, MarketQuoteCache
from app.schemas.market import MarketQuote
from app.services.market_sync import persist_quotes


@pytest.mark.asyncio
async def test_persist_quotes_creates_asset_and_cache(db_session):
    quote = MarketQuote(
        key="bist100",
        name="BIST 100",
        symbol="XU100.IS",
        region="Turkey",
        price=100.0,
        currency="TRY",
        change=1.0,
        change_percent=1.0,
        timestamp=datetime(2026, 8, 18, tzinfo=timezone.utc),
    )

    await persist_quotes(db_session, [quote])
    await persist_quotes(db_session, [quote])

    asset = (
        await db_session.execute(
            select(MarketAsset).where(MarketAsset.key == "bist100")
        )
    ).scalar_one()
    cached_quote = (
        await db_session.execute(
            select(MarketQuoteCache).where(MarketQuoteCache.asset_id == asset.id)
        )
    ).scalar_one()

    assert asset.currency == "TRY"
    assert cached_quote.price == 100.0
    assert cached_quote.change_percent == 1.0
    assert len(
        (
            await db_session.execute(
                select(MarketQuoteCache).where(
                    MarketQuoteCache.asset_id == asset.id
                )
            )
        ).scalars().all()
    ) == 1
