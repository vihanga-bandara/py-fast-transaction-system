from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Transaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    account_id: int
    created_datetime: datetime
    amount: int