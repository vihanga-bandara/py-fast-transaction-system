from datetime import datetime

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    userid: int
    accountid: int


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    created_datetime: datetime