from typing import List, Optional

import pydantic

import mith


class Product(pydantic.BaseModel):
    id: str = mith.PrimaryKey()
    name: str


class APIContract:
    @mith.query("getProducts")
    async def get_products(self) -> List[Product]:
        ...

    @mith.mutation("addProduct")
    async def add_product(self, name: str) -> Optional[str]:
        ...

    @mith.resolve_reference(Product)
    async def resolve_product(self, id: str) -> Optional[Product]:
        ...
