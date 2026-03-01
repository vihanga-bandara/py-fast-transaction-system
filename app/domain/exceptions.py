class AccountNotFoundError(Exception):
    def __init__(self, account_id: int | str):
        self.account_id = account_id
        super().__init__(f"Account with ID {account_id} not found")