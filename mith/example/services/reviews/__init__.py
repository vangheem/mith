import mith
from mith.example.types.reviews import APIContract

from .api import API
from .repositories import ReviewsRepository
from .settings import Settings


def includeme(config: mith.Configuration) -> None:
    """
    Called on startup to configure service
    """
    config.add_service(
        service_id="reviews",
        settings_type=Settings,
        repositories=[ReviewsRepository],
        apis=[mith.implements_api(APIContract, API)],
        dependencies=["products", "users"],
    )
