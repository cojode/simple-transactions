import aiohttp

import aiohttp
from aiohttp import ClientError


class AuthClientServiceError(Exception): ...


class AuthClientConnectionError(AuthClientServiceError): ...


class AuthClientUnexpectedError(AuthClientServiceError): ...


class AuthClientFailedVerificationError(AuthClientServiceError): ...


class AuthClientBadTokenError(AuthClientFailedVerificationError): ...


class AuthClientUsernameNotExistError(AuthClientFailedVerificationError): ...


class AuthClientService:
    BASE_URL = "http://auth:8000/api/v1/auth"

    @staticmethod
    async def prefetch_transaction(
        from_user_username: str, from_user_token: str, to_user_username: str
    ) -> tuple[dict, dict]:
        user_from = await AuthClientService.verify_token(
            from_user_username, from_user_token
        )
        user_to = await AuthClientService.is_username_exists(to_user_username)
        return (user_from, user_to)

    @staticmethod
    async def verify_token(username: str, token: str):
        url = f"{AuthClientService.BASE_URL}/verify-token"
        headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"username": username}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise AuthClientBadTokenError
                    else:
                        raise AuthClientUnexpectedError
            except ClientError:
                raise AuthClientConnectionError

    @staticmethod
    async def is_username_exists(username: str):
        url = f"{AuthClientService.BASE_URL}/username/{username}"

        headers = {"accept": "*/*"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        raise AuthClientUsernameNotExistError
                    else:
                        raise AuthClientUnexpectedError
            except ClientError:
                raise AuthClientConnectionError
