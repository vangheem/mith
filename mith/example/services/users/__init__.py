import polymith

from .api import API
from .settings import Settings
from .repositories import UsersRepository
from pm_example.types.products import APIContract


def includeme(config: polymith.Configuration) -> None:
    """
    Called on startup to configure service
    """
    config.add_service(
        service_id="users",
        settings_type=Settings,
        repositories=[UsersRepository],
        apis=[polymith.implements_api(APIContract, API)],
    )
