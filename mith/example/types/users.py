import pydantic

import mith


class User(pydantic.BaseModel):
    id: str
    name: str


class APIContract:
    @mith.mutation("addUser")
    async def add_user(self, name: str) -> None:
        ...
