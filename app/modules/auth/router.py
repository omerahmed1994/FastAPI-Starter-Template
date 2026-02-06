"""Auth router: login and password recovery endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.common.models import Message
from app.modules.auth import service
from app.modules.auth.schemas import NewPassword, Token
from app.modules.users.schemas import UserPublic

router = APIRouter(prefix="/login", tags=["login"])


@router.post("/access-token", response_model=Token)
def login_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    return service.login_access_token(session=session, form_data=form_data)


@router.post("/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    return service.get_current_user_profile(current_user)


@router.post("/password-recovery/{email}", response_model=Message)
def recover_password(email: str, session: SessionDep) -> Message:
    message = service.send_password_recovery(email=email, session=session)
    return Message(message=message)


@router.post("/reset-password/", response_model=Message)
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    message = service.reset_password(session=session, body=body)
    return Message(message=message)


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    # Keep existing logic in place by delegating to utilities directly
    from app.utils import generate_reset_password_email, generate_password_reset_token
    from fastapi import HTTPException

    user = service.users_service.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )

