from __future__ import annotations

import argparse
import asyncio
import glob
import hashlib
import os
import random
import secrets
from datetime import datetime, timedelta, timezone
from typing import Iterable

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure all ORM models are imported/registered before touching Base.metadata / queries.
import app.infrastructure.models  # noqa: F401

from app.infrastructure.database import async_session_factory
from app.infrastructure.models.account import Account
from app.infrastructure.models.transaction import Transaction
from app.infrastructure.models.user import User
from app.infrastructure.models.user_permission import UserPermission
from app.infrastructure.models.user_role import UserRole


DB_FILENAME = "transaction_system.db"


def _assert_single_db_file() -> str:
    """
    Ensures exactly one *.db exists in the current working directory and it is transaction_system.db.
    Returns the absolute path to the DB file.
    """
    cwd = os.getcwd()
    db_files = sorted(glob.glob(os.path.join(cwd, "*.db")))

    if len(db_files) == 0:
        raise SystemExit(
            f"No .db files found in {cwd!r}.\n"
            f"Expected exactly one SQLite file: {DB_FILENAME!r}."
        )

    if len(db_files) > 1:
        names = ", ".join(os.path.basename(p) for p in db_files)
        raise SystemExit(
            f"Multiple .db files found in {cwd!r}: {names}\n"
            "Please keep only one .db file (the intended target database) and retry."
        )

    only_db = os.path.basename(db_files[0])
    if only_db != DB_FILENAME:
        raise SystemExit(
            f"Found one .db file {only_db!r}, but this project is configured to use {DB_FILENAME!r}.\n"
            "Either rename the file to transaction_system.db or update your engine URL accordingly."
        )

    return os.path.abspath(db_files[0])


def _chunked(seq: list[dict], size: int) -> Iterable[list[dict]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _make_password_pair() -> tuple[str, str]:
    """
    Returns (password_hash, password_salt). Not secure/auth-ready, just deterministic-enough seed data.
    """
    salt = secrets.token_hex(16)
    digest = hashlib.sha256(f"placeholder-password:{salt}".encode("utf-8")).hexdigest()
    return digest, salt


async def _ensure_roles(session: AsyncSession) -> dict[str, int]:
    """
    Creates 3 roles if they don't exist, returns mapping role_name -> role_id.
    """
    wanted = {
        "controller": "Can review and control transactions",
        "admin": "Full administrative access",
        "approver": "Can approve transactions",
    }

    existing = await session.execute(select(UserRole.id, UserRole.name))
    existing_map = {name: role_id for role_id, name in existing.all()}

    to_insert = []
    for name, desc in wanted.items():
        if name not in existing_map:
            to_insert.append({"name": name, "description": desc})

    if to_insert:
        await session.execute(insert(UserRole), to_insert)
        await session.commit()

    # Re-load ids (SQLite autoincrement ids are only known after insert/commit)
    rows = await session.execute(select(UserRole.id, UserRole.name))
    return {name: role_id for role_id, name in rows.all() if name in wanted}


async def _count(session: AsyncSession, model) -> int:
    return int(await session.scalar(select(func.count()).select_from(model)))


async def populate(users_x: int, accounts_x: int, transactions_n: int, seed: int | None) -> None:
    _assert_single_db_file()

    rng = random.Random(seed)

    async with async_session_factory() as session:
        # Basic sanity: ensure tables exist (your app normally calls create_all on startup).
        # If you want to create tables here too, uncomment the import + create_all logic in your app startup.

        role_ids = await _ensure_roles(session)

        # --- 1) Users ---
        users_before = await _count(session, User)
        if users_x > 0:
            now = datetime.now(timezone.utc)
            user_rows: list[dict] = []
            for i in range(users_x):
                pwd_hash, pwd_salt = _make_password_pair()
                user_rows.append(
                    {
                        "name": f"User {users_before + i + 1}",
                        "email": f"user{users_before + i + 1}@example.local",
                        "password_hash": pwd_hash,
                        "password_salt": pwd_salt,
                        "created_datetime": now - timedelta(days=rng.randint(0, 365)),
                    }
                )

            # Insert users in batches
            for batch in _chunked(user_rows, size=2000):
                await session.execute(insert(User), batch)
                await session.commit()

        # Get all user ids (we’ll assign permissions & transactions against these)
        user_ids = list((await session.execute(select(User.id))).scalars().all())
        if not user_ids:
            raise SystemExit("No users available after population step. Cannot proceed.")

        # --- 2) Accounts ---
        accounts_before = await _count(session, Account)
        if accounts_x > 0:
            account_rows: list[dict] = []
            for i in range(accounts_x):
                account_rows.append(
                    {
                        "name": f"Account {accounts_before + i + 1}",
                        "amount": rng.randint(0, 2_000_000),
                    }
                )
            for batch in _chunked(account_rows, size=2000):
                await session.execute(insert(Account), batch)
                await session.commit()

        account_ids = list((await session.execute(select(Account.id))).scalars().all())
        if not account_ids:
            raise SystemExit("No accounts available after population step. Cannot proceed.")

        # --- 3) UserPermission (randomly assign a role per user) ---
        # Strategy: 1 permission row per user (you can change to multi-role per user if you want).
        perm_before = await _count(session, UserPermission)
        if perm_before == 0:
            role_choices = list(role_ids.values())
            if not role_choices:
                raise SystemExit("Role table empty. Cannot assign permissions.")

            perm_rows: list[dict] = []
            for uid in user_ids:
                perm_rows.append(
                    {
                        "user_id": uid,
                        "user_role_id": rng.choice(role_choices),
                    }
                )

            for batch in _chunked(perm_rows, size=5000):
                await session.execute(insert(UserPermission), batch)
                await session.commit()

        # --- 4) Transactions ---
        if transactions_n > 0:
            now = datetime.now(timezone.utc)
            tx_rows: list[dict] = []
            for _ in range(transactions_n):
                tx_rows.append(
                    {
                        "user_id": rng.choice(user_ids),
                        "account_id": rng.choice(account_ids),
                        "created_datetime": now - timedelta(seconds=rng.randint(0, 90 * 24 * 3600)),
                    }
                )

                # Stream commits to avoid holding 50k dicts unnecessarily if you bump this higher
                if len(tx_rows) >= 5000:
                    await session.execute(insert(Transaction), tx_rows)
                    await session.commit()
                    tx_rows.clear()

            if tx_rows:
                await session.execute(insert(Transaction), tx_rows)
                await session.commit()

    print(
        "Done.\n"
        f"Inserted (requested): users={users_x}, accounts={accounts_x}, transactions={transactions_n}\n"
        "Roles ensured: controller, admin, approver\n"
        f"DB file: {DB_FILENAME}"
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Populate transaction_system.db with seed data.")
    p.add_argument("--users", type=int, default=1000, help="How many users to insert (default: 1000)")
    p.add_argument("--accounts", type=int, default=200, help="How many accounts to insert (default: 200)")
    p.add_argument(
        "--transactions",
        type=int,
        default=50_000,
        help="How many transactions to insert (default: 50000)",
    )
    p.add_argument("--seed", type=int, default=None, help="Optional RNG seed for reproducibility")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(
        populate(
            users_x=args.users,
            accounts_x=args.accounts,
            transactions_n=args.transactions,
            seed=args.seed,
        )
    )