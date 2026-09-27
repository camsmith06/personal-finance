from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.category import Category


class Direction(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class Payer(StrEnum):
    ME = "ME"
    PARTNER = "PARTNER"


class SharingType(StrEnum):
    PERSONAL = "PERSONAL"
    SHARED = "SHARED"


class TransactionSource(StrEnum):
    CSV = "CSV"
    MANUAL = "MANUAL"


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "amount_minor_units >= 0", name="ck_transactions_amount_non_negative"
        ),
        CheckConstraint("currency = 'USD'", name="ck_transactions_currency_supported"),
        CheckConstraint(
            "direction IN ('DEBIT', 'CREDIT')", name="ck_transactions_direction"
        ),
        CheckConstraint("payer IN ('ME', 'PARTNER')", name="ck_transactions_payer"),
        CheckConstraint(
            "sharing_type IN ('PERSONAL', 'SHARED')",
            name="ck_transactions_sharing_type",
        ),
        CheckConstraint("source IN ('CSV', 'MANUAL')", name="ck_transactions_source"),
        CheckConstraint(
            "partner_share_minor_units IS NULL OR partner_share_minor_units >= 0",
            name="ck_transactions_partner_share_non_negative",
        ),
        CheckConstraint(
            "partner_share_minor_units IS NULL OR "
            "partner_share_minor_units <= amount_minor_units",
            name="ck_transactions_partner_share_not_exceed_amount",
        ),
        Index("ix_transactions_transaction_date", "transaction_date"),
        Index("ix_transactions_category_id", "category_id"),
        Index("ix_transactions_sharing_type", "sharing_type"),
        Index("ix_transactions_payer", "payer"),
        Index(
            "uq_transactions_deduplication_key",
            "deduplication_key",
            unique=True,
            postgresql_where=text("deduplication_key IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    merchant: Mapped[str | None] = mapped_column(String(255))
    amount_minor_units: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="USD"
    )
    direction: Mapped[Direction] = mapped_column(String(10), nullable=False)
    payer: Mapped[Payer] = mapped_column(String(10), nullable=False)
    sharing_type: Mapped[SharingType] = mapped_column(String(10), nullable=False)
    partner_share_minor_units: Mapped[int | None] = mapped_column(Integer)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT")
    )
    source: Mapped[TransactionSource] = mapped_column(String(10), nullable=False)
    deduplication_key: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category: Mapped["Category | None"] = relationship(back_populates="transactions")
