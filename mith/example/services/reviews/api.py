from typing import List, Optional

from mith.example.types.reviews import Review

from .repositories import ReviewsRepository


class API:
    async def get_reviews(
        self, repo: ReviewsRepository, author_id: str
    ) -> List[Review]:
        return await repo.get_reviews(author_id=author_id)

    async def add_review(
        self, repo: ReviewsRepository, author_id: str, body: str, product_id: str
    ) -> Optional[str]:
        await repo.add_review(author_id=author_id, body=body, product_id=product_id)
        return "success"
