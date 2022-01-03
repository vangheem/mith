from typing import Type

import pydantic

from ._base import BaseRepository
from .alchemy import RowMapper, SQLAlchemyTableRepository
from .config import Configuration, implements_api, mutation, query, resolve_reference


def Reference(model_type: Type[pydantic.BaseModel]) -> Type[pydantic.BaseModel]:
    fields = {}
    for f_name, field in model_type.__fields__.items():
        if not field.field_info.extra.get("primary_key"):
            continue
        fields[f_name] = (model_type.__annotations__[f_name], field.field_info)

    mdl = pydantic.create_model(model_type.__name__, **fields)
    mdl.__config__.reference = True
    return mdl


def PrimaryKey():
    return pydantic.Field(primary_key=True)


__all__ = (
    "SQLAlchemyTableRepository",
    "RowMapper",
    "Reference",
    "Configuration",
    "query",
    "mutation",
    "implements_api",
    "BaseRepository",
    "resolve_reference",
)
