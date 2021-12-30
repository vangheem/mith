from typing import TypeVar

import pydantic

from ._base import BaseRepository

SettingType = TypeVar("SettingType", bound=pydantic.BaseSettings)
RepoType = TypeVar("RepoType", bound=BaseRepository)
