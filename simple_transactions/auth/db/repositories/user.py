from simple_transactions.auth.db.dao import ExtendedCRUDRepository, repository_for

from simple_transactions.auth.db.models.user import UserModel

@repository_for(UserModel)
class UserRepository(ExtendedCRUDRepository[UserModel]):
    async def is_user_exists(self, user_id: int) -> bool:
        return await self.exists(id=user_id)
    
    async def is_username_exists(self, user_username: str) -> bool:
        return await self.exists(username=user_username)

    async def create_user(self, **user_fields) -> UserModel:
        return await self.create(**user_fields)

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        return await self.find_by_id(item_id=user_id)
    
    async def get_user_by_username(self, user_username: str) -> UserModel | None:
        return await self.find_one(username=user_username)

    async def update_user_by_username(
        self, user_to_update_username: str, **new_fields
    ) -> int:
        return await self.update(fields=new_fields, username=user_to_update_username)