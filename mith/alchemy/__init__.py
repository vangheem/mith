from typing import Dict, Generic, Optional, Type, TypeVar, Union

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

    def __init__(self, pg_settings: PostgreSQLSettings, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.pg_settings = pg_settings

    async def initialize(self) -> None:
        dsn = self.pg_settings.postgres_writer_dsn.replace(
            "postgres://", "postgresql://"
        )
        engine = sqlalchemy.create_engine(dsn)
        self.table.metadata.bind = engine
        self.table.metadata.reflect()
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
        self,
        table: Type[sqlalchemy.orm.DeclarativeMeta],
        model_type: RowMapperType,
        mapped_fields: Optional[Dict[str, str]] = None,
    ):
        self.table = table
        self.model_type = model_type
        self.mapped_fields = mapped_fields or {}

    def __call__(self, record: Record) -> RowMapperType:
        inst_data = {}
        for from_, to_ in self.mapped_fields.items():
            inst_data[to_] = record[from_]
        for f_name in self.model_type.__fields__.keys():
            if f_name in inst_data:
                continue
            if f_name in record:
                inst_data[f_name] = record[f_name]
        return self.model_type.parse_obj(inst_data)
