from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.exceptions import AccountNotFoundError
from app.infrastructure.repositories.transaction import TransactionRepository


@pytest.mark.asyncio
async def test_get_all_returns_transactions():
    now = datetime.now(timezone.utc)

    session = AsyncMock()
    result = Mock()
    result.scalars.return_value.all.return_value = [
        SimpleNamespace(id=1, user_id=11, account_id=21, amount=300, created_datetime=now),
        SimpleNamespace(id=2, user_id=12, account_id=22, amount=-40, created_datetime=now),
    ]
    session.execute.return_value = result

    repo = TransactionRepository(session=session)

    transactions = await repo.get_all()

    assert [t.id for t in transactions] == [1, 2]
    assert [t.amount for t in transactions] == [300, -40]


@pytest.mark.asyncio
async def test_create_transaction_returns_transaction_when_account_exists():
    fixed_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    @asynccontextmanager
    async def begin_ctx():
        yield

    session = AsyncMock()
    session.begin = Mock(return_value=begin_ctx())
    session.scalar.return_value = 9
    session.add = Mock()

    def add_side_effect(trn):
        trn.created_datetime = fixed_time

    session.add.side_effect = add_side_effect

    repo = TransactionRepository(session=session)

    transaction = await repo.create_transaction(
        transaction_id=123,
        user_id=2,
        account_id=9,
        amount=150,
    )

    assert transaction.id == 123
    assert transaction.user_id == 2
    assert transaction.account_id == 9
    assert transaction.amount == 150
    assert transaction.created_datetime == fixed_time
    session.scalar.assert_awaited_once()
    session.add.assert_called_once()
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_transaction_raises_when_account_missing():
    @asynccontextmanager
    async def begin_ctx():
        yield

    session = AsyncMock()
    session.begin = Mock(return_value=begin_ctx())
    session.scalar.return_value = None
    session.add = Mock()

    repo = TransactionRepository(session=session)

    with pytest.raises(AccountNotFoundError):
        await repo.create_transaction(
            transaction_id=123,
            user_id=2,
            account_id=404,
            amount=150,
        )

    session.add.assert_not_called()
    session.flush.assert_not_awaited()
