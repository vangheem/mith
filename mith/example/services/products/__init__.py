import mith
from mith.example.types.products import APIContract

from .api import API
from .repositories import ProductsRepository
from .settings import Settings


def includeme(config: mith.Configuration) -> None:
    """
    Called on startup to configure service
    """
    config.add_service(
        service_id="products",
        settings_type=Settings,
        repositories=[ProductsRepository],
        apis=[mith.implements_api(APIContract, API)],
    )
