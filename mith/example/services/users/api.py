from typing import List

from mith.example.types.reviews import Review

from .repositories import UsersRepository


class API:
    async def get_reviews(self, repo: UsersRepository, author_id: str) -> List[Review]:
        return repo.get_reviews(author_id=author_id)
