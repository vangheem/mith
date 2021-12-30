import mith
from mith.example.types.products import APIContract

from .api import API
from .repositories import UsersRepository
from .settings import Settings


def includeme(config: mith.Configuration) -> None:
    """
    Called on startup to configure service
    """
    config.add_service(
        service_id="users",
        settings_type=Settings,
        repositories=[UsersRepository],
        apis=[mith.implements_api(APIContract, API)],
    )
