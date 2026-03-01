from typing import Protocol, List, Optional
from app.domain.entities.account import Account

class IAccountRepository(Protocol):

    async def get_by_id(self, account_id: int) -> Optional[Account]:
        ...
    async def get_all(self) -> List[Account]:
        ...