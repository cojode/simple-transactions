import os

from passlib.context import CryptContext

from jose import jwt, JWTError
from datetime import timedelta, datetime
import pytz

from simple_transactions.auth.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityServiceError(Exception): ...
class SecurityServiceBadTokenError(SecurityServiceError): ...

class SecurityService:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict, 
        expires_delta: timedelta = timedelta(seconds=settings.SIMPLE_TRANSACTIONS_AUTH_DEFAULT_JWT_EXPIRES_SECONDS)):
        to_encode = data.copy()
        expire = datetime.now(pytz.timezone("UTC")) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, 
            key=settings.SIMPLE_TRANSACTIONS_AUTH_SECRET_KEY, 
            algorithm=settings.SIMPLE_TRANSACTIONS_AUTH_ENCRYPT_ALGORITHM
        )
    
    @staticmethod
    def verify_and_get_username(token: str) -> str:
        try:
            payload = jwt.decode(token, settings.SIMPLE_TRANSACTIONS_AUTH_SECRET_KEY, 
                                 algorithms=[settings.SIMPLE_TRANSACTIONS_AUTH_ENCRYPT_ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise SecurityServiceBadTokenError
        except JWTError:
            raise SecurityServiceBadTokenError
        
        return username