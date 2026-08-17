"""create market asset and quote cache models

Revision ID: 20260818_0001
Revises:
Create Date: 2026-08-18
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260818_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "market_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("region", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_market_assets_key"), "market_assets", ["key"], unique=True)

    op.create_table(
        "market_quote_cache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("change", sa.Float(), nullable=True),
        sa.Column("change_percent", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["market_assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_id", "timestamp", name="uq_market_quote_asset_timestamp"),
    )
    op.create_index(
        op.f("ix_market_quote_cache_asset_id"),
        "market_quote_cache",
        ["asset_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_market_quote_cache_asset_id"), table_name="market_quote_cache")
    op.drop_table("market_quote_cache")
    op.drop_index(op.f("ix_market_assets_key"), table_name="market_assets")
    op.drop_table("market_assets")
