from datetime import datetime

from pydantic import BaseModel


class TransactionCreateRequest(BaseModel):
    user_id: int
    account_id: int
    amount: int


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    created_datetime: datetime
    amount: int