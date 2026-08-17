from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models.market import MarketAsset, MarketQuoteCache


@pytest.mark.asyncio
async def test_market_asset_and_quote_cache_relationship(db_session):
    asset = MarketAsset(
        key="sp500",
        name="S&P 500",
        symbol="^GSPC",
        region="United States",
        currency="USD",
        created_at=datetime.now(timezone.utc),
    )
    asset.quotes.append(
        MarketQuoteCache(
            price=5000.0,
            change=25.0,
            change_percent=0.5,
            timestamp=datetime.now(timezone.utc),
        )
    )

    db_session.add(asset)
    await db_session.commit()

    result = await db_session.execute(
        select(MarketAsset).where(MarketAsset.key == "sp500")
    )
    stored_asset = result.scalar_one()

    assert stored_asset.symbol == "^GSPC"
    assert len(stored_asset.quotes) == 1
    assert stored_asset.quotes[0].price == 5000.0
