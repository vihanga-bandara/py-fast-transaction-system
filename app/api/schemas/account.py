from pydantic import BaseModel

class AccountResponse(BaseModel):
    id: int
    name: str
    balance: int

class AccountCreateRequest(BaseModel):
    name: str