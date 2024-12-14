from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from punq import Container

router = APIRouter()

from simple_transactions.auth.container.container import init_container

from simple_transactions.auth.services.auth import (
    AuthService,
    AuthServiceUsernameAlreadyRegisteredError,
    AuthServiceFailedAuthenticationError,
    AuthServiceBadTokenError,
    AuthServiceUsernameNotRegisteredError,
)

http_bearer = HTTPBearer()


@router.get("/username/{username}", status_code=status.HTTP_200_OK)
async def get_user_by_username(
    username: str, container: Container = Depends(init_container)
):
    auth_service: AuthService = container.resolve(AuthService)
    try:
        return await auth_service.get_user_by_username(username=username)
    except AuthServiceUsernameNotRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exists."
        )


@router.post("/verify-token", status_code=status.HTTP_200_OK)
async def verify_token(
    username: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    container: Container = Depends(init_container),
):
    auth_service: AuthService = container.resolve(AuthService)
    try:
        return await auth_service.verify_token_and_get_user(
            username, credentials.credentials
        )
    except (AuthServiceBadTokenError, AuthServiceUsernameNotRegisteredError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed.",
        )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    username: str,
    password: str,
    balance: int,
    container: Container = Depends(init_container),
):
    auth_service: AuthService = container.resolve(AuthService)
    try:
        return await auth_service.register_user(
            username=username, password=password, balance=balance
        )
    except AuthServiceUsernameAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered.",
        )


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    container: Container = Depends(init_container),
):
    auth_service: AuthService = container.resolve(AuthService)
    try:
        return await auth_service.login_user(
            username=form_data.username, password=form_data.password
        )
    except AuthServiceFailedAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed for user {form_data.username}: invalid credentials.",
        )


@router.post("/change-password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(
    username: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    new_password: str = Form(...),
    container: Container = Depends(init_container),
):
    auth_service: AuthService = container.resolve(AuthService)
    try:
        await auth_service.update_user_password(
            username, credentials.credentials, new_password
        )
    except (AuthServiceUsernameNotRegisteredError, AuthServiceBadTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Password change request failed for user {username}: invalid credentials.",
        )
