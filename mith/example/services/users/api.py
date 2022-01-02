from typing import List, Optional

from mith.example.types.users import User

from .repositories import UsersRepository


class API:
    async def get_users(self, repo: UsersRepository) -> List[User]:
        return await repo.get_users()

    async def add_user(self, repo: UsersRepository, name: str) -> Optional[str]:
        await repo.add_user(name)
        return "success"
