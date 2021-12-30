from typing import List

import polymith
import pydantic

from .products import Product
from .users import User


class Review(pydantic.BaseModel):
    id: str
    body: str
    author: User = polymith.Reference(User)
    product: Product = polymith.Reference(Product)


class APIContract:
    @polymith.query("getReviews")
    async def get_reviews(self, author_id: str) -> List[Review]:
        ...

    @polymith.mutation("addReview")
    async def add_review(self, author_id: str, body: str, product_id: str) -> None:
        ...
