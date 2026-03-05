from typing import AsyncGenerator
from fastapi import Depends
from snowflake import SnowflakeGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.AccountService import AccountService
from app.application.services.TransactionService import TransactionService
from app.infrastructure.database import async_session_factory
from app.infrastructure.repositories.account import AccountRepository
from app.infrastructure.repositories.transaction import TransactionRepository


# Generator to yield DB sessions and close them safely after the request
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


# Accounts
def get_account_repository(session: AsyncSession = Depends(get_db_session)) -> AccountRepository:
    return AccountRepository(session=session)


def get_account_service(repository: AccountRepository = Depends(get_account_repository)) -> AccountService:
    return AccountService(account_repository=repository)


# Transaction
def get_transaction_repository(session: AsyncSession = Depends(get_db_session)) -> TransactionRepository:
    return TransactionRepository(session=session)


def get_transaction_service(
        repository: TransactionRepository = Depends(get_transaction_repository)) -> TransactionService:
    return TransactionService(transaction_repository=repository)

# Users
