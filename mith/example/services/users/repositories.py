from typing import List

import sqlalchemy

import mith
from mith.example.types.users import User

UsersTable = sqlalchemy.Table(
    "users",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
)


review_row_mapper = mith.RowMapper[User](UsersTable, User)


class UsersRepository(mith.SQLAlchemyTableRepository):
    table = UsersTable

    async def get_users(self) -> List[User]:
        return [review_row_mapper(row_model) for row_model in await self.query.all()]
