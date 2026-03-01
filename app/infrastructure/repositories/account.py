from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.application.interfaces.account_repo import IAccountRepository
from app.domain.entities.account import Account as AccountDto
from app.infrastructure.models.account import Account

class AccountRepository(IAccountRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, account_id: int) -> Optional[AccountDto]:
        query = select(Account).where(Account.id == account_id)
        result = await self._session.execute(query)
        db_account = result.scalar_one_or_none()

        if not db_account:
            return None

        return AccountDto.model_validate(db_account)

    async def get_all(self) -> List[Account]:
        stmt = select(Account)
        result = await self._session.execute(stmt)

        db_accounts = result.scalars().all()

        return [AccountDto.model_validate(acc) for acc in db_accounts]