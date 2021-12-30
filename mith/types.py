import pydantic
from typing import TypeVar
from ._base import BaseRepository


SettingType = TypeVar("SettingType", bound=pydantic.BaseSettings)
RepoType = TypeVar("RepoType", bound=BaseRepository)
