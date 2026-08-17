"""Persistent market asset and quote cache models."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MarketAsset(Base):
    __tablename__ = "market_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    region: Mapped[str] = mapped_column(String(64), nullable=False)
    currency: Mapped[str | None] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    quotes: Mapped[list["MarketQuoteCache"]] = relationship(
        back_populates="asset",
        cascade="all, delete-orphan",
    )


class MarketQuoteCache(Base):
    __tablename__ = "market_quote_cache"
    __table_args__ = (
        UniqueConstraint("asset_id", "timestamp", name="uq_market_quote_asset_timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("market_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    price: Mapped[float | None] = mapped_column(Float)
    change: Mapped[float | None] = mapped_column(Float)
    change_percent: Mapped[float | None] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    asset: Mapped[MarketAsset] = relationship(back_populates="quotes")
