from typing import List

from pm_example.types.reviews import Review
from .repositories import ReviewsRepository


class API:
    async def get_reviews(
        self, repo: ReviewsRepository, author_id: str
    ) -> List[Review]:
        return repo.get_reviews(author_id=author_id)
