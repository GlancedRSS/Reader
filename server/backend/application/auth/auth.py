"""Application service orchestrating authentication operations."""

from uuid import UUID

import structlog
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.app import settings
from backend.domain import (
    AuthDomain,
    AuthValidationDomain,
    InvalidCredentialsError,
    InvalidPasswordError,
)
from backend.infrastructure.auth.ip_utils import IPUtils
from backend.infrastructure.auth.security import (
    PasswordHasher,
    generate_csrf_token,
)
from backend.infrastructure.repositories.session import (
    revoke_session_cookie,
    verify_session_cookie,
)
from backend.infrastructure.repositories.user import UserRepository
from backend.models import User
from backend.schemas.core import ResponseMessage
from backend.schemas.core.common import ListResponse
from backend.schemas.domain.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RegistrationRequest,
    SessionResponse,
)

logger = structlog.get_logger()


class AuthApplication:
    """Application service that orchestrates authentication operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the auth application with database session and services.

        Args:
            db: Async database session for repository operations.

        """
        from backend.infrastructure.repositories.session import (
            SessionRepository,
        )

        self.db = db
        self.password_hasher = PasswordHasher()
        self.auth_domain = AuthDomain(password_hasher=self.password_hasher)
        self.validation = AuthValidationDomain()
        self.session_repository = SessionRepository(db)
        self.user_repository = UserRepository(db)

    async def register(self, user_data: RegistrationRequest) -> ResponseMessage:
        """Register a new user account.

        Args:
            user_data: The registration request containing username and password.

        Returns:
            Response message indicating successful account creation.

        Raises:
            HTTPException: If validation fails or username already exists.

        """
        try:
            username = self.validation.validate_username_format(
                user_data.username
            )

            self.validation.validate_password_format(user_data.password)

            username_exists = await self.user_repository.username_exists(
                username
            )
            self.validation.validate_username_unique(username_exists)
        except ValueError as e:
            if "already exists" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=str(e),
                ) from None
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from None

        user_count = await self.user_repository.count_users()
        is_first_user = user_count == 0

        password_hash = self.password_hasher.hash_password(user_data.password)
        is_admin = is_first_user and self.auth_domain.FIRST_USER_IS_ADMIN

        user = await self.user_repository.create_user(
            username=username,
            password_hash=password_hash,
            first_name=None,
            last_name=None,
            is_admin=is_admin,
        )

        if is_admin:
            logger.info(
                "First user registered - assigned admin privileges",
                user_id=user.id,
                username=username,
            )

        return ResponseMessage(message="Account created successfully")

    async def login(
        self, user_data: LoginRequest, request: Request
    ) -> tuple[ResponseMessage, tuple[str, str]]:
        """Sign in user and create session.

        Args:
            user_data: The login request containing username and password.
            request: The HTTP request to extract IP and user agent from.

        Returns:
            Tuple of (response message, (session_token, csrf_token)).

        Raises:
            HTTPException: If credentials are invalid or account status is invalid.

        """
        ip_utils = IPUtils()
        ip_address = ip_utils.get_client_ip(request)

        user = await self.user_repository.find_by_username(user_data.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        try:
            self.auth_domain.verify_credentials(user, user_data.password)
            self.auth_domain.update_last_login(user)
        except InvalidCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            ) from None

        await self.user_repository.update_user(
            user, {"last_login": user.last_login}
        )

        active_session_count = (
            await self.session_repository.get_active_session_count(user.id)
        )
        should_revoke = self.auth_domain.check_session_limit(
            active_session_count
        )

        if should_revoke:
            revoked = await self.session_repository.revoke_oldest_session(
                user.id
            )
            if revoked:
                logger.info(
                    f"Revoked oldest session for user {user.id} due to session limit"
                )

        user_agent = request.headers.get("user-agent")
        session, session_token = await self.session_repository.create_session(
            user_id=user.id, user_agent=user_agent, ip_address=ip_address
        )

        csrf_token = generate_csrf_token()

        logger.info(
            f"User logged in successfully: {user.username} (session: {session.session_id})"
        )

        response_message = ResponseMessage(message="Login successful")
        return response_message, (session_token, csrf_token)

    async def logout(self, request: Request) -> ResponseMessage:
        """Sign out user and clear session.

        Args:
            request: The HTTP request containing session cookie.

        Returns:
            Response message indicating successful logout.

        """
        session_token = request.cookies.get(settings.session_cookie_name)

        if session_token:
            success = await revoke_session_cookie(session_token, self.db)
            if success:
                logger.info(
                    "Logged out session", session_token_prefix=session_token[:8]
                )
            else:
                logger.warning("Logout attempted with invalid session cookie")
        else:
            logger.warning("Logout attempted without session cookie")

        return ResponseMessage(message="Successfully logged out")

    async def change_password(
        self,
        password_data: PasswordChangeRequest,
        current_user: User,
    ) -> ResponseMessage:
        """Change user password.

        Args:
            password_data: The password change request with current and new password.
            current_user: The authenticated user.

        Returns:
            Response message indicating successful password change.

        Raises:
            HTTPException: If current password is invalid.

        """
        try:
            self.auth_domain.change_user_password(
                current_user,
                password_data.current_password,
                password_data.new_password,
            )
        except InvalidPasswordError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            ) from None

        await self.session_repository.revoke_all_user_sessions(current_user.id)

        return ResponseMessage(message="Password changed successfully")

    async def get_sessions(
        self,
        current_user: User,
        current_session_id: UUID | None,
    ) -> ListResponse[SessionResponse]:
        """Get list of user sessions.

        Args:
            current_user: The authenticated user.
            current_session_id: The ID of the current session to mark.

        Returns:
            List of user sessions.

        """
        sessions = await self.session_repository.get_user_sessions(
            current_user.id
        )

        return ListResponse[SessionResponse](
            data=[
                SessionResponse(
                    session_id=session.session_id,
                    created_at=session.created_at,
                    last_used=session.last_used,
                    expires_at=session.expires_at,
                    user_agent=session.user_agent,
                    ip_address=str(session.ip_address)
                    if session.ip_address
                    else None,
                    current=session.session_id == current_session_id,
                )
                for session in sessions
            ]
        )

    async def revoke_session(
        self, session_id: UUID, current_user: User
    ) -> ResponseMessage:
        """Revoke a specific session.

        Args:
            session_id: The ID of the session to revoke.
            current_user: The authenticated user.

        Returns:
            Response message indicating successful session revocation.

        Raises:
            HTTPException: If session is not found (404).

        """
        deleted_count = await self.session_repository.revoke_session_by_id(
            current_user.id, session_id
        )

        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        return ResponseMessage(message="Session removed successfully")

    async def get_current_session_id(self, session_token: str) -> UUID:
        """Get session ID from session token.

        Args:
            session_token: The session token to verify.

        Returns:
            The session ID.

        Raises:
            ValueError: If session is invalid or expired.

        """
        session = await verify_session_cookie(session_token, self.db)
        if not session:
            raise ValueError("Invalid or expired session")
        return session.session_id
