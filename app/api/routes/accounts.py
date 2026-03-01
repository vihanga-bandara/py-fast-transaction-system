from typing import List
from fastapi import APIRouter, Depends
from app.api.dependencies import get_account_service
from app.api.schemas.account import AccountResponse
from app.application.services.AccountService import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=List[AccountResponse])
async def get_all_accounts(service: AccountService = Depends(get_account_service)):
    return await service.get_all_accounts()
