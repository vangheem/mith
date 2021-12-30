import polymith
from pm_example.types.products import Product
from typing import List
import sqlalchemy

ProductsTable = sqlalchemy.Table(
    "products",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
)

review_row_mapper = polymith.RowMapper(ProductsTable, Product)


class ProductsRepository(polymith.SQLAlchemyTableRepository):
    table = ProductsTable

    async def get_products(self) -> List[Product]:
        return [review_row_mapper(row_model) for row_model in await self.query.all()]
