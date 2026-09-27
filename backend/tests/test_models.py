from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Category, Direction, Payer, SharingType, Transaction


def create_transaction(**overrides: object) -> Transaction:
    values = {
        "transaction_date": date(2026, 9, 20),
        "description": "Coffee",
        "amount_minor_units": 500,
        "currency": "USD",
        "direction": Direction.DEBIT,
        "payer": Payer.ME,
        "sharing_type": SharingType.PERSONAL,
        "source": "MANUAL",
    }
    values.update(overrides)
    return Transaction(**values)


def test_valid_category_can_be_persisted(db_session: Session) -> None:
    category = Category(name="Groceries")
    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert category.created_at is not None
    assert category.updated_at is not None


def test_valid_transaction_can_be_persisted(db_session: Session) -> None:
    transaction = create_transaction()
    db_session.add(transaction)
    db_session.commit()

    assert transaction.id is not None
    assert transaction.created_at is not None
    assert transaction.updated_at is not None


def test_transaction_can_reference_category(db_session: Session) -> None:
    category = Category(name="Utilities")
    transaction = create_transaction(category=category)
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    assert transaction.category_id == category.id
    assert transaction.category is category


@pytest.mark.parametrize(
    "field,value",
    [
        ("direction", "INVALID"),
        ("payer", "INVALID"),
        ("sharing_type", "INVALID"),
    ],
)
def test_invalid_enum_values_are_rejected(
    db_session: Session, field: str, value: str
) -> None:
    db_session.add(create_transaction(**{field: value}))

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_negative_amount_is_rejected(db_session: Session) -> None:
    db_session.add(create_transaction(amount_minor_units=-1))

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_partner_share_greater_than_amount_is_rejected(
    db_session: Session,
) -> None:
    db_session.add(
        create_transaction(amount_minor_units=500, partner_share_minor_units=501)
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_duplicate_category_names_are_rejected(db_session: Session) -> None:
    db_session.add_all([Category(name="Travel"), Category(name="Travel")])

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_duplicate_non_null_deduplication_keys_are_rejected(
    db_session: Session,
) -> None:
    db_session.add_all(
        [
            create_transaction(deduplication_key="csv-row-1"),
            create_transaction(deduplication_key="csv-row-1"),
        ]
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_multiple_null_deduplication_keys_are_allowed(db_session: Session) -> None:
    db_session.add_all(
        [
            create_transaction(description="First"),
            create_transaction(description="Second"),
        ]
    )
    db_session.commit()
