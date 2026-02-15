"""User authentication and session management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status

from backend.application.auth import AuthApplication, CookieManager
from backend.core.app import settings
from backend.core.database import get_db
from backend.core.fastapi import get_user_from_request_state
from backend.models import User
from backend.schemas.core import ResponseMessage
from backend.schemas.core.common import ListResponse
from backend.schemas.domain.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RegistrationRequest,
    SessionResponse,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=ResponseMessage,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with a username and password.",
    tags=["Authentication"],
)
async def register(
    user_data: RegistrationRequest,
    db=Depends(get_db),
) -> ResponseMessage:
    """Register a new user account."""
    auth_app = AuthApplication(db)
    return await auth_app.register(user_data)


@router.post(
    "/login",
    response_model=ResponseMessage,
    summary="Login",
    description="Login with your username and password to start a session.",
    tags=["Authentication"],
)
async def login(
    user_data: LoginRequest,
    request: Request,
    response: Response,
    db=Depends(get_db),
) -> ResponseMessage:
    """Login with username and password to start a session."""
    auth_app = AuthApplication(db)
    cookie_manager = CookieManager()

    result, (session_token, csrf_token) = await auth_app.login(
        user_data, request
    )

    cookies = cookie_manager.generate_session_cookies(session_token, csrf_token)
    response.set_cookie(**cookies["session_cookie"])
    response.set_cookie(**cookies["csrf_cookie"])

    return result


@router.post(
    "/logout",
    response_model=ResponseMessage,
    summary="Logout",
    description="Logout from your current session and clear authentication cookies.",
    tags=["Authentication"],
)
async def logout(
    request: Request,
    response: Response,
    db=Depends(get_db),
) -> ResponseMessage:
    """Logout from current session and clear authentication cookies."""
    auth_app = AuthApplication(db)
    cookie_manager = CookieManager()

    result = await auth_app.logout(request)

    cookies = cookie_manager.generate_clear_cookies()
    response.delete_cookie(**cookies["session_cookie"])
    response.delete_cookie(**cookies["csrf_cookie"])

    return result


@router.post(
    "/change-password",
    response_model=ResponseMessage,
    summary="Change password",
    description="Change your password after verifying your current password.",
    tags=["Authentication"],
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_user_from_request_state),
    db=Depends(get_db),
) -> ResponseMessage:
    """Change password after verifying current password."""
    auth_app = AuthApplication(db)
    return await auth_app.change_password(password_data, current_user)


@router.get(
    "/sessions",
    response_model=ListResponse[SessionResponse],
    summary="List active sessions",
    description="List your active sessions across all devices.",
    tags=["Authentication"],
)
async def get_user_sessions(
    request: Request,
    current_user: User = Depends(get_user_from_request_state),
    db=Depends(get_db),
) -> ListResponse[SessionResponse]:
    """List your active sessions across all devices."""
    auth_app = AuthApplication(db)
    session_token = request.cookies.get(settings.session_cookie_name)
    if not session_token:
        current_session_id = None
    else:
        try:
            current_session_id = await auth_app.get_current_session_id(
                session_token
            )
        except ValueError:
            current_session_id = None

    return await auth_app.get_sessions(current_user, current_session_id)


@router.delete(
    "/sessions/{session_id}",
    response_model=ResponseMessage,
    summary="Revoke session",
    description="Revoke a specific active session on another device.",
    tags=["Authentication"],
)
async def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_user_from_request_state),
    db=Depends(get_db),
) -> ResponseMessage:
    """Revoke a specific active session on another device."""
    auth_app = AuthApplication(db)
    return await auth_app.revoke_session(session_id, current_user)
