import uuid
from typing import List, Optional

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
        return [
            review_row_mapper(row_model)
            for row_model in await self.fetch(self.table.select())
        ]

    async def get_user(self, id: str) -> Optional[User]:
        results = await self.fetch(
            self.table.select().filter(UsersTable.c.id == id).limit(1)
        )
        if len(results) > 0:
            return review_row_mapper(results[0])

    async def add_user(self, name: str) -> None:
        await self.execute(self.table.insert().values(id=uuid.uuid4().hex, name=name))
