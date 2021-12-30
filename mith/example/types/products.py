import pydantic
import polymith


class Product(pydantic.BaseModel):
    id: str
    name: str


class APIContract:
    @polymith.mutation("addProduct")
    async def add_product(self, name: str) -> None:
        ...
