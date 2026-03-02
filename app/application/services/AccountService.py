from app.api.schemas.account import AccountCreateRequest
from app.application.interfaces.account_repo import IAccountRepository
from app.domain.entities.account import Account
from app.domain.exceptions import AccountNotFoundError


class AccountService:
    def __init__(self, repository: IAccountRepository):
        self._accountRepository = repository

    async def get_account_by_id(self, account_id: int) -> Account:
        account = await self._accountRepository.get_by_id(account_id)
        if not account:
            raise AccountNotFoundError(account_id)
        return account

    async def get_all_accounts(self) -> list[Account]:
        accounts = await self._accountRepository.get_all()
        return accounts

    async def get_account_by_name(self, account_name: str) -> Account:
        account = await self._accountRepository.get_by_name(account_name)
        if not account:
            raise AccountNotFoundError(account_name)
        return account

    async def create_account(self, account_name: str) -> Account:
        return await self._accountRepository.create_account(account_name)
