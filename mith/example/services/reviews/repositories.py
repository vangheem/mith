import polymith
from pm_example.types.reviews import Review
from typing import List
import sqlalchemy
import sqlalchemy.orm


ReviewsTable = sqlalchemy.Table(
    "reviews",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column(
        "author_id", sqlalchemy.String, sqlalchemy.ForeignKey("author.id")
    ),
    sqlalchemy.Column(
        "product_id", sqlalchemy.String, sqlalchemy.ForeignKey("product.id")
    ),
)


review_row_mapper = polymith.RowMapper(ReviewsTable, Review)


class ReviewsRepository(polymith.SQLAlchemyTableRepository):
    table = ReviewsTable

    async def get_reviews(self, author_id: str) -> List[Review]:
        return [
            review_row_mapper(row_model)
            for row_model in await self.query.filter(author_id == author_id)
        ]
