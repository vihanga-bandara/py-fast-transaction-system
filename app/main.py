from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import accounts, transactions
from app.infrastructure.database import engine
from app.infrastructure.models.base import Base
from app.domain.exceptions import AccountNotFoundError

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Transaction API", lifespan=lifespan)

# Register one middleware, will move this later
@app.exception_handler(AccountNotFoundError)
async def account_not_found_handler(request: Request, exc: AccountNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )

# Register routers
app.include_router(accounts.router)
app.include_router(transactions.router)