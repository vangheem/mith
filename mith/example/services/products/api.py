from typing import List, Optional

from mith.example.types.products import Product

from .repositories import ProductsRepository


class API:
    async def get_products(self, repo: ProductsRepository) -> List[Product]:
        return await repo.get_products()

    async def add_product(self, repo: ProductsRepository, name: str) -> Optional[str]:
        await repo.add_product(name)
        return "success"

    async def resolve_product(
        self, repo: ProductsRepository, id: str
    ) -> Optional[Product]:
        return await repo.get_product(id=id)
