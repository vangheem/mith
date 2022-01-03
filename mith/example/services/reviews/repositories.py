import uuid
from typing import List

import asyncpg
import sqlalchemy
import sqlalchemy.orm
from pydantic.main import BaseModel
from mith.example.types.reviews import Review, UserReference, ProductReference

import mith

ReviewsTable = sqlalchemy.Table(
    "reviews",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column(
        "author_id", sqlalchemy.String, sqlalchemy.ForeignKey("users.id")
    ),
    sqlalchemy.Column(
        "product_id", sqlalchemy.String, sqlalchemy.ForeignKey("products.id")
    ),
)


def review_row_mapper(record: asyncpg.Record) -> Review:
    return Review(
        id=record["id"],
        body=record["body"],
        author=UserReference(id=record["author_id"]),
        product=ProductReference(id=record["product_id"]),
    )


class ReviewsRepository(mith.SQLAlchemyTableRepository):
    table = ReviewsTable

    async def get_reviews(self, author_id: str) -> List[Review]:
        return [
            review_row_mapper(row_model)
            for row_model in await self.fetch(
                self.table.select().filter(author_id == author_id)
            )
        ]

    async def add_review(self, author_id: str, body: str, product_id: str) -> str:
        await self.execute(
            self.table.insert().values(
                id=uuid.uuid4().hex,
                author_id=author_id,
                body=body,
                product_id=product_id,
            )
        )
