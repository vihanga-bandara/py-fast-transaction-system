from typing import Protocol, List
from app.domain.entities.transaction import Transaction


class ITransactionRepository(Protocol):

    async def get_all(self) -> List[Transaction]:
        ...
    async def create_transaction(self, transaction_id: int, user_id: int, account_id: int,
                                 amount: int) -> Transaction:
        ...