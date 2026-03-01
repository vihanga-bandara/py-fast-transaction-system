# Py Fast Transaction System

FastAPI + SQLAlchemy (async) demo project using SQLite (`transaction_system.db`) with Users, Roles, Accounts, Permissions, and Transactions.

## Seed Database
Populates roles (`controller`, `admin`, `approver`), users, accounts, permissions, and transactions.

#### python populate-db.py --users 10000 --accounts 2000 --transactions 50000 --seed 123

## Tech Stack

- **Python**: 3.14+
- **API**: FastAPI
- **ASGI server**: Uvicorn
- **DB/ORM**: SQLAlchemy 2.x (async) + aiosqlite
- **Database**: SQLite (`transaction_system.db`)

## Patterns & Techniques Used
- **Clean Architecture-ish layout**: separates concerns into `api/` (HTTP), `application/` (use-cases/services), `domain/` (entities + business exceptions), `infrastructure/` (DB + repositories).
- **Dependency Injection (FastAPI `Depends`)**: services/repositories/sessions are wired via dependency functions instead of being created inside route handlers.
- **Repository Pattern**: repositories encapsulate SQLAlchemy queries and return domain/data models rather than leaking ORM details everywhere.
- **Service Layer (Use-cases)**: application services coordinate repository calls and enforce business rules (e.g., “not found” -> domain exception).
- **Async SQLAlchemy**: uses `AsyncEngine` / `AsyncSession` for non-blocking DB access.
- **SQLite for local dev**: quick setup, single-file database.
- **Schema/Model separation**: API response/request schemas are kept separate from ORM models to avoid tight coupling.
- **Startup/Lifespan table creation (dev-only)**: tables are created on app startup for local SQLite runs (will move to alembic later)