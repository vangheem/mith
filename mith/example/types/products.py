import pydantic

import mith


class Product(pydantic.BaseModel):
    id: str
    name: str


class APIContract:
    @mith.mutation("addProduct")
    async def add_product(self, name: str) -> None:
        ...
