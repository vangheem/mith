from typing import Generic, Type, TypeVar, Union

import asyncpg
import pydantic
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql
from asyncpg import Record

from .._base import BaseRepository
from ..settings import PostgreSQLSettings
from .utils import compile_sql

QueryType = Union[
    sqlalchemy.sql.Update,
    sqlalchemy.sql.Delete,
    sqlalchemy.sql.Select,
    sqlalchemy.sql.Insert,
]


class SQLAlchemyTableRepository(BaseRepository):
    table: sqlalchemy.Table

    def __init__(self, settings: PostgreSQLSettings, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.settings = settings

    async def initialize(self) -> None:
        dsn = self.settings.postgres_writer_dsn.replace("postgres://", "postgresql://")
        engine = sqlalchemy.create_engine(dsn)
        self.table.metadata.create_all(engine)

    async def finalize(self) -> None:
        ...

    async def execute(self, query: QueryType) -> None:
        sql, query_args, _ = compile_sql(query)
        await self.db_pool.execute(sql, *query_args)

    async def fetch(self, query: QueryType) -> asyncpg.Record:
        sql, query_args, _ = compile_sql(query)
        return await self.db_pool.fetch(sql, *query_args)


RowMapperType = TypeVar("RowMapperType", bound=pydantic.BaseModel)


class RowMapper(Generic[RowMapperType]):
    def __init__(
        self, table: Type[sqlalchemy.orm.DeclarativeMeta], model_type: RowMapperType
    ):
        self.table = table
        self.model_type = model_type

    def __call__(self, record: Record) -> RowMapperType:
        ...
