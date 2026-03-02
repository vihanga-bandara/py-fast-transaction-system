from snowflake import SnowflakeGenerator

from app.application.interfaces.transaction_repo import ITransactionRepository
from app.domain.entities.transaction import Transaction


class TransactionService:
    def __init__(self, transaction_repository: ITransactionRepository, id_generator: SnowflakeGenerator):
        self._transaction_repository = transaction_repository
        self._id_generator = id_generator(42)

    async def get_all_transactions(self):
        return await self._transaction_repository.get_all()

    async def create_transaction(self, user_id: int, account_id: int, amount: int) -> Transaction:
        return await self._transaction_repository.create_transaction(
            transaction_id=next(self._id_generator),
            user_id=user_id,
            account_id=account_id,
            amount=amount,
        )