from pydantic import BaseModel

class AccountResponse(BaseModel):
    id: int
    name: str
    amount: int

class AccountCreateRequest(BaseModel):
    name: str