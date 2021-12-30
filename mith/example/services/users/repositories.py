import polymith
from pm_example.types.users import User
from typing import List
import sqlalchemy


UsersTable = sqlalchemy.Table(
    "users",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
)


review_row_mapper = polymith.RowMapper[User](UsersTable, User)


class UsersRepository(polymith.SQLAlchemyTableRepository):
    table = UsersTable

    async def get_users(self) -> List[User]:
        return [review_row_mapper(row_model) for row_model in await self.query.all()]
