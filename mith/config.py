from typing import List, TypeVar, Any
import os

from .types import RepoType, SettingType
from .utils import resolve_dotted_name
import abc


PassThroughDecType = TypeVar("PassThroughDecType")


class _config_decorator:
    def __call__(self, func: PassThroughDecType) -> PassThroughDecType:
        if not hasattr(func, "__mith__"):
            func.__mith__ = {}
        self.register(func)
        return func

    @abc.abstractmethod
    def register(self, func: PassThroughDecType) -> None:
        raise NotImplementedError


class query(_config_decorator):
    def __init__(self, name: str):
        self.name = name

    def register(self, func: PassThroughDecType) -> None:
        func.__mith__.update({"type": "query", "name": self.name})


class mutation(_config_decorator):
    def __init__(self, name: str):
        self.name = name

    def register(self, func: PassThroughDecType):
        func.__mith__.update({"type": "mutation", "name": self.name})


class APIDefinition:
    def __init__(self, contract, implementor):
        self.contract = contract
        self.implementor = implementor


def implements_api(contract: Any, implementor: Any):
    """
    Should validate correct API
    """
    return APIDefinition(contract, implementor)


class ServiceConfiguration:
    def __init__(
        self,
        *,
        service_id: str,
        settings_type: SettingType,
        repositories: List[RepoType],
        apis: List[APIDefinition],
        dependencies: List[str],
    ):
        self.service_id = service_id
        self.settings_type = settings_type
        self.repositories = repositories
        self.apis = apis
        self.dependencies = dependencies


class Configuration:
    def __init__(self):
        self.services: List[ServiceConfiguration] = []

    def add_service(
        self,
        *,
        service_id: str,
        settings_type: SettingType,
        repositories: List[RepoType],
        apis: List[APIDefinition],
        dependencies: List[str] = None,
    ) -> None:
        self.services.append(
            ServiceConfiguration(
                service_id=service_id,
                settings_type=settings_type,
                repositories=repositories,
                apis=apis,
                dependencies=dependencies or [],
            )
        )


def load_configuration_from_environment() -> Configuration:
    config = Configuration()

    for env_name, env_value in os.environ.items():
        if not env_name.startswith("SERVICE_"):
            continue
        # nothing special about name, just care about loading value
        module = resolve_dotted_name(env_value)
        if not hasattr(module, "includeme"):
            raise Exception(
                f"{env_name}:{env_value} missing `def includeme(config):` definition"
            )

        module.includeme(config)

    return config
