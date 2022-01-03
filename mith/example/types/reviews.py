from typing import List, Optional

import pydantic

import mith

from .products import Product
from .users import User


UserReference = mith.Reference(User)
ProductReference = mith.Reference(Product)


class Review(pydantic.BaseModel):
    id: str = mith.PrimaryKey()
    body: str
    author: UserReference
    product: ProductReference


class APIContract:
    @mith.query("getReviews")
    async def get_reviews(self, author_id: str) -> List[Review]:
        ...

    @mith.mutation("addReview")
    async def add_review(
        self, author_id: str, body: str, product_id: str
    ) -> Optional[str]:
        ...
