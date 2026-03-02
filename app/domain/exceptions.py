class AccountNotFoundError(Exception):
    def __init__(self, account_id: int | str):
        self.account_id = account_id
        super().__init__(f"Account with ID {account_id} not found")

class AccountCreationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)