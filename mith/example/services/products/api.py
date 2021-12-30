from typing import List

from mith.example.types.reviews import Review

from .repositories import ProductsRepository


class API:
    async def get_reviews(
        self, repo: ProductsRepository, author_id: str
    ) -> List[Review]:
        return repo.get_products(author_id=author_id)
