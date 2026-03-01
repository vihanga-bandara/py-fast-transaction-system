from pydantic import BaseModel

class AccountResponse(BaseModel):
    id: int
    name: str
    amount: int

