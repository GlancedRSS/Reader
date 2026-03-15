import asyncio
import getpass
import sys

from backend.core.database import AsyncSessionLocal
from backend.infrastructure.auth.security import PasswordHasher
from backend.infrastructure.repositories import UserRepository


async def reset_password(username: str) -> None:
    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)

        user = await repo.find_by_username(username)
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

        if len(password) < 8:
            print("Password must be at least 8 characters")
            sys.exit(1)

        hasher = PasswordHasher()
        password_hash = hasher.hash_password(password)

        await repo.update_user(user, {"password_hash": password_hash})
        await db.commit()

        print("Password updated successfully")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m backend.cli.reset_password <username>")
        sys.exit(1)

    username = sys.argv[1]
    asyncio.run(reset_password(username))


if __name__ == "__main__":
    main()
