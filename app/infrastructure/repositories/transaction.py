from typing import List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.transaction_repo import ITransactionRepository
from app.domain.entities.transaction import Transaction as TransactionDto
from app.domain.exceptions import AccountNotFoundError
from app.infrastructure.models.account import Account
from app.infrastructure.models.transaction import Transaction


class TransactionRepository(ITransactionRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> List[TransactionDto]:
        stmt = select(Transaction)
        result = await self._session.execute(stmt)
        transactions = result.scalars().all()

        return [TransactionDto.model_validate(transaction) for transaction in transactions]

    async def create_transaction(self, transaction_id: int, user_id: int, account_id: int, amount: int) -> TransactionDto:
        async with self._session.begin():
            update_stmt = (
                update(Account)
                .where(Account.id == account_id)
                .values(balance=Account.balance + amount)
                .returning(Account.id)
            )
            updated_account_id = await self._session.scalar(update_stmt)

            if updated_account_id is None:
                raise AccountNotFoundError(account_id)

            trn = Transaction(
                id=transaction_id,
                user_id=user_id,
                account_id=account_id,
                amount=amount,
            )
            self._session.add(trn)
            await self._session.flush()

        return TransactionDto.model_validate(trn)
