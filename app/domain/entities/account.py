from pydantic import BaseModel, ConfigDict
from typing import Optional

class Account(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    name: str
    balance: int