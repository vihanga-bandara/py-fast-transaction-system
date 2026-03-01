from typing import List
from fastapi import APIRouter, Depends
from app.api.dependencies import get_account_service
from app.api.schemas.account import AccountResponse
from app.application.services.AccountService import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=List[AccountResponse])
async def get_all_accounts(service: AccountService = Depends(get_account_service)):
    return await service.get_all_accounts()

@router.get("/id/{account_id}", response_model=AccountResponse)
async def get_account_by_id(account_id: int, service: AccountService = Depends(get_account_service)):
    return await service.get_account_by_id(account_id)

@router.get("/name/{account_name}", response_model=AccountResponse)
async def get_account_by_name(account_name: str, service: AccountService = Depends(get_account_service)):
    return await service.get_account_by_name(account_name)