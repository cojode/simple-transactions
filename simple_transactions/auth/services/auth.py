from simple_transactions.auth.db.repositories.user import UserRepository
from simple_transactions.auth.db.models.user import UserModel

from simple_transactions.auth.services.security import (
    SecurityService,
    SecurityServiceBadTokenError
)
from simple_transactions.auth.services.utils import model_row_to_dict

from loguru import logger

class AuthServiceError(Exception): ...
class AuthServiceUsernameAlreadyRegisteredError(AuthServiceError): ...
class AuthServiceFailedAuthenticationError(AuthServiceError): ...
class AuthServiceUsernameNotRegisteredError(AuthServiceError): ...
class AuthServiceBadTokenError(AuthServiceError): ...

class AuthService:
    def __init__(self, user_repository: UserRepository, security_service: SecurityService):
        self.user_repository: UserRepository = user_repository
        self.security_service: SecurityService = security_service
    
    async def authenticate_user(self, username: str, password: str) -> UserModel:
        user = await self.user_repository.get_user_by_username(username)
        if not (user and self.security_service.verify_password(password, user.hashed_password)):
            logger.info(f'Authentication failed for user {username}')
            raise AuthServiceFailedAuthenticationError
        return user

    async def verify_username_token(self, username: str, token: str):
        if not await self.user_repository.is_username_exists(username):
            logger.info(f'Unknown username, token rejected for user: {username}')
            raise AuthServiceUsernameNotRegisteredError
        try:
            token_username = self.security_service.verify_and_get_username(token)
        except SecurityServiceBadTokenError:
            logger.info(f'Token extraction failed for user: {username}')
            raise AuthServiceBadTokenError
        if username != token_username:
            logger.info(f'Token extraction failed for user: {username}')
            raise AuthServiceBadTokenError
        
        logger.info(f'Token verified for user: {username}')
        
        
    async def update_user_password(self, username: str, token: str, new_password: str):
        await self.verify_username_token(username, token)
        await self.user_repository.update_user_by_username(
            user_to_update_username=username,
            hashed_password=self.security_service.get_password_hash(new_password)
        )
        logger.info(f'User {username} succesfully changed password.')
        
        
    async def register_user(self, username: str, password: str, balance: int) -> dict:
        if await self.user_repository.is_username_exists(user_username=username):
            logger.info('Registration attempt failed: user with username {username} already registered.')
            raise AuthServiceUsernameAlreadyRegisteredError
        
        user = await self.user_repository.create_user(
            username=username,
            hashed_password=self.security_service.get_password_hash(password),
            balance=balance
        )
        
        output = model_row_to_dict(user)
        output.pop('hashed_password')
        logger.info(f'Registration attempt succeded: new user {output} successfully registered.')
        return output

    async def login_user(self, username: str, password: str) -> UserModel:
        user = await self.authenticate_user(username, password)
        logger.info(f'Login success for username: {username}')
        return {
                'access_token': self.security_service.create_access_token({'sub': user.username}),
                'token_type': 'bearer'
            }
    
