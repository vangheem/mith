import uuid
from typing import List

import sqlalchemy

import mith
from mith.example.types.products import Product

ProductsTable = sqlalchemy.Table(
    "products",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
)

review_row_mapper = mith.RowMapper(ProductsTable, Product)


class ProductsRepository(mith.SQLAlchemyTableRepository):
    table = ProductsTable

    async def get_products(self) -> List[Product]:
        return [
            review_row_mapper(row_model)
            for row_model in await self.fetch(self.table.select())
        ]

    async def add_product(self, name: str) -> None:
        await self.execute(self.table.insert().values(id=uuid.uuid4().hex, name=name))
