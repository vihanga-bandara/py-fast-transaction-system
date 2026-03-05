import pytest
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from sqlalchemy.exc import IntegrityError

from app.domain.exceptions import AccountCreationError
from app.infrastructure.repositories.account import AccountRepository


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_account_missing():
    session = AsyncMock()
    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repo = AccountRepository(session=session)

    account = await repo.get_by_id(account_id=123)

    assert account is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_account_when_found():
    session = AsyncMock()
    db_account = SimpleNamespace(id=1, name="savings", balance=250)
    result = Mock()
    result.scalar_one_or_none.return_value = db_account
    session.execute.return_value = result

    repo = AccountRepository(session=session)

    account = await repo.get_by_id(account_id=1)

    assert account is not None
    assert account.id == 1
    assert account.name == "savings"
    assert account.balance == 250


@pytest.mark.asyncio
async def test_get_by_name_returns_none_when_account_missing():
    session = AsyncMock()
    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repo = AccountRepository(session=session)

    account = await repo.get_by_name(account_name="missing")

    assert account is None
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_returns_accounts():
    session = AsyncMock()
    db_accounts = [
        SimpleNamespace(id=1, name="checking", balance=100),
        SimpleNamespace(id=2, name="savings", balance=250),
    ]
    result = Mock()
    result.scalars.return_value.all.return_value = db_accounts
    session.execute.return_value = result

    repo = AccountRepository(session=session)

    accounts = await repo.get_all()

    assert [acc.name for acc in accounts] == ["checking", "savings"]
    assert [acc.balance for acc in accounts] == [100, 250]


@pytest.mark.asyncio
async def test_create_account_returns_created_account():
    @asynccontextmanager
    async def begin_ctx():
        yield

    session = AsyncMock()
    session.begin = Mock(return_value=begin_ctx())
    session.add = Mock()

    async def refresh_side_effect(db_account):
        db_account.id = 10
        db_account.balance = 0

    session.refresh = AsyncMock(side_effect=refresh_side_effect)

    repo = AccountRepository(session=session)

    account = await repo.create_account(account_name="primary")

    assert account.id == 10
    assert account.name == "primary"
    assert account.balance == 0
    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_account_raises_account_creation_error_on_integrity_error():
    @asynccontextmanager
    async def begin_ctx():
        yield

    session = AsyncMock()
    session.begin = Mock(return_value=begin_ctx())
    session.add = Mock()
    session.flush.side_effect = IntegrityError("INSERT", {}, Exception("duplicate"))

    repo = AccountRepository(session=session)

    with pytest.raises(AccountCreationError):
        await repo.create_account(account_name="duplicate")
