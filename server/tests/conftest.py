"""Pytest configuration and shared fixtures."""

# Set test environment FIRST before any backend imports
import os
import sys
from importlib.metadata import version as get_version

_APP_VERSION = get_version("glanced-reader-server")

os.environ["ENVIRONMENT"] = "test"

# Clean any cached backend modules that might have been imported with wrong settings
for module in list(sys.modules.keys()):
    if module.startswith("backend"):
        del sys.modules[module]

from collections.abc import AsyncGenerator  # noqa: E402
from uuid import uuid4  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from backend.core.app import settings  # noqa: E402
from backend.core.database import AsyncSessionLocal  # noqa: E402
from backend.infrastructure.auth.security import PasswordHasher  # noqa: E402
from backend.main import app  # noqa: E402
from backend.models import User, UserSession  # noqa: E402
from backend.models import User as UserModel  # noqa: E402

# Override environment setting for tests
settings.environment = "test"


# =============================================================================
# Sample Data Fixtures (Unit Tests)
# =============================================================================


@pytest.fixture
def sample_username() -> str:
    """Sample username for tests."""
    return "testuser"


@pytest.fixture
def sample_password() -> str:
    """Sample password for tests (meets requirements)."""
    return "TestPass123"


@pytest.fixture
def sample_user_id() -> str:
    """Sample user ID for tests."""
    return str(uuid4())


@pytest.fixture
def sample_session_id() -> str:
    """Sample session ID for tests."""
    return str(uuid4())


@pytest.fixture
def sample_user_agent() -> str:
    """Sample user agent for tests."""
    return (
        f"Glanced-Reader/{_APP_VERSION} (+https://github.com/glancedrss/reader)"
    )


@pytest.fixture
def sample_ip_address() -> str:
    """Sample IP address for tests."""
    return "192.168.1.1"


# =============================================================================
# Database Fixtures (Integration Tests)
# =============================================================================


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Create a test database session with clean state.

    Wraps each test in a transaction that's rolled back for isolation.
    """
    # Create session with nested transaction for rollback
    async with AsyncSessionLocal() as session:
        # Start a nested transaction (SAVEPOINT)
        await session.begin_nested()
        yield session
        # Rollback to SAVEPOINT
        await session.rollback()
        # Rollback the outer transaction to ensure all changes are discarded
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> UserModel:
    """Create a test user in the database.

    Returns:
        A User instance with username 'testuser_<uuid>' and password 'TestPass123'.
        Note: Each test gets a unique username to avoid conflicts.
    """
    from uuid import uuid4

    password_hasher = PasswordHasher()
    unique_suffix = uuid4().hex[:8]
    user = UserModel(
        username=f"testuser_{unique_suffix}",
        password_hash=password_hasher.hash_password("TestPass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_admin_user(db_session: AsyncSession) -> UserModel:
    """Create a test admin user in the database.

    Returns:
        A User instance with username 'admin_<uuid>' and password 'AdminPass123'.
        Note: Each test gets a unique username to avoid conflicts.
    """
    from uuid import uuid4

    password_hasher = PasswordHasher()
    unique_suffix = uuid4().hex[:8]
    user = UserModel(
        username=f"admin_{unique_suffix}",
        password_hash=password_hasher.hash_password("AdminPass123"),
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# =============================================================================
# HTTP Client Fixtures (Integration Tests)
# =============================================================================


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_db_pool():
    """Clean up database connections between tests to avoid event loop issues."""
    yield
    # Dispose all connections in the pool after each test
    from backend.core.database import engine

    await engine.dispose()


@pytest.fixture(autouse=True)
def mock_arq_client(monkeypatch):
    """Mock ArqClient to avoid needing Redis in tests.

    Integration tests that enqueue background jobs should work without
    an actual Redis connection or running worker.
    """

    async def mock_enqueue(*args, **kwargs):
        """Mock job enqueue that returns a fake job ID."""
        from uuid import uuid4

        return str(uuid4())

    # Patch the ArqClient enqueue_job method
    monkeypatch.setattr(
        "backend.infrastructure.external.arq_client.ArqClient.enqueue_job",
        mock_enqueue,
    )


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient]:
    """Create an async HTTP client for testing FastAPI endpoints.

    Uses ASGI transport to avoid needing a running server.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(
    async_client: AsyncClient,
) -> AsyncGenerator[AsyncClient]:
    """Create an authenticated HTTP client with a valid session.

    Returns:
        An AsyncClient with a valid session cookie for a test user.
        Note: Test data is not cleaned up to avoid event loop issues.
    """
    import secrets
    import uuid
    from datetime import UTC, datetime, timedelta

    from backend.core.app import settings
    from backend.infrastructure.auth.security import (
        PasswordHasher,
        generate_csrf_token,
        hash_token,
    )

    # Create a separate connection for auth setup (needs to be committed)
    async with AsyncSessionLocal() as auth_db:
        password_hasher = PasswordHasher()
        unique_suffix = uuid.uuid4().hex[:8]
        user = User(
            username=f"authuser_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        auth_db.add(user)
        await auth_db.flush()

        # Generate session token
        session_id = uuid.uuid4()
        secret_token = secrets.token_urlsafe(32)
        session_token = f"{session_id}.{secret_token}"
        cookie_hash = hash_token(session_token)

        # Generate CSRF token
        csrf_token = generate_csrf_token()

        # Create session
        expires_at = datetime.now(UTC) + timedelta(
            seconds=settings.session_cookie_max_age
        )
        session = UserSession(
            user_id=user.id,
            session_id=session_id,
            cookie_hash=cookie_hash,
            expires_at=expires_at,
            user_agent="Test Client",
            ip_address="127.0.0.1",
        )
        auth_db.add(session)
        await auth_db.commit()

    # Set session and CSRF cookies on the client
    async_client.cookies.set("session_id", session_token)
    async_client.cookies.set(settings.csrf_cookie_name, csrf_token)

    # Set default headers to include CSRF token for state-changing requests
    async_client.headers.update({"X-CSRF-Token": csrf_token})

    yield async_client
    # Clear cookies after test
    async_client.cookies.pop("session_id", None)
    async_client.cookies.pop(settings.csrf_cookie_name, None)
