from typing import List

from fastapi import APIRouter
from fastapi.params import Depends

from app.api.dependencies import get_transaction_service
from app.api.schemas.transaction import TransactionResponse, TransactionCreateRequest
from app.application.services.TransactionService import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=List[TransactionResponse])
async def get_all_transactions(service: TransactionService = Depends(get_transaction_service)):
    return await service.get_all_transactions()

@router.post("", response_model=TransactionResponse)
async def create_transaction(request: TransactionCreateRequest, service: TransactionService = Depends(get_transaction_service)):
    return await service.create_transaction(request.user_id, request.account_id, request.amount)