from typing import List, Optional

import pydantic

import mith


class User(pydantic.BaseModel):
    id: str = mith.PrimaryKey()
    name: str


class APIContract:
    @mith.query("getUsers")
    async def get_users(self) -> List[User]:
        ...

    @mith.mutation("addUser")
    async def add_user(self, name: str) -> Optional[str]:
        ...

    @mith.resolve_reference(User)
    async def resolve_user(self, id: str) -> Optional[User]:
        ...
