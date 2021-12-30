import pydantic
import polymith


class User(pydantic.BaseModel):
    id: str
    name: str


class APIContract:
    @polymith.mutation("addUser")
    async def add_user(self, name: str) -> None:
        ...
