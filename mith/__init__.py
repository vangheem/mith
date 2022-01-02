from typing import Type

import pydantic

from ._base import BaseRepository
from .alchemy import RowMapper, SQLAlchemyTableRepository
from .config import Configuration, implements_api, mutation, query


def Reference(model_type: Type[pydantic.BaseModel]):
    return pydantic.Field(reference=True, model_type=model_type)


__all__ = (
    "SQLAlchemyTableRepository",
    "RowMapper",
    "Reference",
    "Configuration",
    "query",
    "mutation",
    "implements_api",
    "BaseRepository",
)
