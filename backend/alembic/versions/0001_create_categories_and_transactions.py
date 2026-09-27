"""create categories and transactions

Revision ID: 0001_categories_transactions
Revises:
Create Date: 2026-09-20

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_categories_transactions"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("merchant", sa.String(length=255), nullable=True),
        sa.Column("amount_minor_units", sa.Integer(), nullable=False),
        sa.Column(
            "currency", sa.String(length=3), server_default="USD", nullable=False
        ),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("payer", sa.String(length=10), nullable=False),
        sa.Column("sharing_type", sa.String(length=10), nullable=False),
        sa.Column("partner_share_minor_units", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=10), nullable=False),
        sa.Column("deduplication_key", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount_minor_units >= 0",
            name="ck_transactions_amount_non_negative",
        ),
        sa.CheckConstraint(
            "currency = 'USD'",
            name="ck_transactions_currency_supported",
        ),
        sa.CheckConstraint(
            "direction IN ('DEBIT', 'CREDIT')",
            name="ck_transactions_direction",
        ),
        sa.CheckConstraint(
            "payer IN ('ME', 'PARTNER')",
            name="ck_transactions_payer",
        ),
        sa.CheckConstraint(
            "sharing_type IN ('PERSONAL', 'SHARED')",
            name="ck_transactions_sharing_type",
        ),
        sa.CheckConstraint(
            "source IN ('CSV', 'MANUAL')",
            name="ck_transactions_source",
        ),
        sa.CheckConstraint(
            "partner_share_minor_units IS NULL OR partner_share_minor_units >= 0",
            name="ck_transactions_partner_share_non_negative",
        ),
        sa.CheckConstraint(
            "partner_share_minor_units IS NULL OR "
            "partner_share_minor_units <= amount_minor_units",
            name="ck_transactions_partner_share_not_exceed_amount",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name="fk_transactions_category_id_categories",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_transactions_transaction_date",
        "transactions",
        ["transaction_date"],
    )
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_sharing_type", "transactions", ["sharing_type"])
    op.create_index("ix_transactions_payer", "transactions", ["payer"])
    op.create_index(
        "uq_transactions_deduplication_key",
        "transactions",
        ["deduplication_key"],
        unique=True,
        postgresql_where=sa.text("deduplication_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_transactions_deduplication_key", table_name="transactions")
    op.drop_index("ix_transactions_payer", table_name="transactions")
    op.drop_index("ix_transactions_sharing_type", table_name="transactions")
    op.drop_index("ix_transactions_category_id", table_name="transactions")
    op.drop_index("ix_transactions_transaction_date", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("categories")
