# importing it here so it gets captured in main.py to be registered for importing the necessary tables and creating them.

from app.infrastructure.models.account import Account
from app.infrastructure.models.transaction import Transaction
from app.infrastructure.models.user import User
from app.infrastructure.models.user_role import UserRole
from app.infrastructure.models.user_permission import UserPermission