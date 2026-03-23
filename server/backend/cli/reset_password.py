import asyncio
import getpass
import sys

import structlog

from backend.core.database import AsyncSessionLocal
from backend.domain.auth.validation import AuthValidationDomain
from backend.infrastructure.auth.security import PasswordHasher
from backend.infrastructure.repositories import (
    SessionRepository,
    UserRepository,
)


async def reset_password(username: str) -> None:
    logger = structlog.get_logger()

    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)

        user = await user_repo.find_by_username(username)
        if not user:
            print(f"User '{username}' not found")
            sys.exit(1)

        print(f"Resetting password for user: {user.username}")

        password = getpass.getpass("Enter new password: ")
        if not password:
            print("Password cannot be empty")
            sys.exit(1)

        confirm = getpass.getpass("Confirm new password: ")
        if password != confirm:
            print("Passwords do not match")
            sys.exit(1)

        try:
            AuthValidationDomain.validate_password_format(password)
        except ValueError as e:
            print(str(e))
            sys.exit(1)

        hasher = PasswordHasher()
        password_hash = hasher.hash_password(password)

        await user_repo.update_user(user, {"password_hash": password_hash})
        await session_repo.revoke_all_user_sessions(user.id)
        await db.commit()

        logger.info(
            "Password reset via CLI",
            user_id=user.id,
            username=user.username,
        )

        print("Password updated successfully. All sessions have been revoked.")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m backend.cli.reset_password <username>")
        sys.exit(1)

    username = sys.argv[1]
    asyncio.run(reset_password(username))


if __name__ == "__main__":
    main()
