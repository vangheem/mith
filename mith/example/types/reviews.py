from typing import List, Optional

import pydantic

import mith

from .products import Product
from .users import User


class Review(pydantic.BaseModel):
    id: str
    body: str
    author: User = mith.Reference(User)
    product: Product = mith.Reference(Product)


class APIContract:
    @mith.query("getReviews")
    async def get_reviews(self, author_id: str) -> List[Review]:
        ...

    @mith.mutation("addReview")
    async def add_review(
        self, author_id: str, body: str, product_id: str
    ) -> Optional[str]:
        ...
