from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.AccountService import AccountService
from app.infrastructure.database import async_session_factory
from app.infrastructure.repositories.account import AccountRepository

# Generator to yield DB sessions and close them safely after the request
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

# Accounts
def get_account_repository(session: AsyncSession = Depends(get_db_session)) -> AccountRepository:
    return AccountRepository(session=session)

def get_account_service(repository: AccountRepository = Depends(get_account_repository)) -> AccountService:
    return AccountService(repository=repository)


# Transaction


# Users and Permissions