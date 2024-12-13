from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from punq import Container

router = APIRouter()

from simple_transactions.auth.container.container import init_container

from simple_transactions.auth.services.auth import (
    AuthService,
    AuthServiceUsernameAlreadyRegisteredError,
    AuthServiceFailedAuthenticationError,
    AuthServiceBadTokenError,
    AuthServiceUsernameNotRegisteredError
)

http_bearer = HTTPBearer()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(username: str, password: str, container: Container = Depends(init_container)):
    auth_service: AuthService = container.resolve(AuthService)
    try:
        return await auth_service.register_user(username=username, password=password)
    except AuthServiceUsernameAlreadyRegisteredError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already registered.')

@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), container: Container = Depends(init_container)):
    auth_service: AuthService = container.resolve(AuthService)
    try:
        return await auth_service.login_user(username=form_data.username, password=form_data.password)
    except AuthServiceFailedAuthenticationError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Authentication failed for user {form_data.username}: invalid credentials.')

@router.post("/change-password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(username: str = Form(...), credentials: HTTPAuthorizationCredentials = Depends(http_bearer), new_password: str = Form(...), container: Container = Depends(init_container)):
    auth_service: AuthService = container.resolve(AuthService)
    try:
        await auth_service.update_user_password(username, credentials.credentials, new_password)
    except (AuthServiceUsernameNotRegisteredError, AuthServiceBadTokenError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Password change request failed for user {username}: invalid credentials.')
    