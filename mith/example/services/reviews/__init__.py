import polymith

from .api import API
from .settings import Settings
from .repositories import ReviewsRepository
from pm_example.types.reviews import APIContract


def includeme(config: polymith.Configuration) -> None:
    """
    Called on startup to configure service
    """
    config.add_service(
        service_id="reviews",
        settings_type=Settings,
        repositories=[ReviewsRepository],
        apis=[polymith.implements_api(APIContract, API)],
        dependencies=["products", "users"],
    )
