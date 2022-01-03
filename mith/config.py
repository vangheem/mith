import abc
import inspect
import os
from typing import Any, Dict, List, Optional, TypeVar, Type

import asyncpg
import pydantic

from mith.settings import PostgreSQLSettings

from .const import EndpointType
from .types import RepoType, SettingType
from .utils import resolve_dotted_name

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
        func.__mith__.update({"type": EndpointType.QUERY, "name": self.name})


class mutation(_config_decorator):
    def __init__(self, name: str):
        self.name = name

    def register(self, func: PassThroughDecType):
        func.__mith__.update({"type": EndpointType.MUTATION, "name": self.name})


class resolve_reference(_config_decorator):
    def __init__(self, model_type: Type[pydantic.BaseModel]):
        self.model_type = model_type

    def register(self, func: PassThroughDecType):
        func.__mith__.update(
            {
                "type": EndpointType.RESOLVE_REFERENCE,
                "model_type": self.model_type,
                "name": f"Resolve{self.model_type.__name__}",
            }
        )


class APIDefinition:
    def __init__(self, contract, implementor):
        self.contract = contract
        self.implementor = implementor

    def __repr__(self) -> str:
        return f"<APIDefinition {self.contract.__module__}.{self.contract.__name__} />"


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
        self.settings = settings_type()
        self.repositories = repositories
        self.apis = apis
        self.dependencies = dependencies

    def __repr__(self) -> str:
        return f"<ServiceConfiguration {self.service_id} {self.apis} />"


def call_injectable(
    callable_: Any,
    configuration: "Configuration",
    additional: Optional[Dict[str, Any]] = None,
) -> Any:
    additional_by_type = {}
    if additional is None:
        additional_by_name = {}
    else:
        additional_by_name = additional.copy()
    additional_by_name.update({"configuration": configuration})
    for aval in additional.values():
        additional_by_type[type(aval)] = aval

    sig = inspect.signature(callable_)
    kwargs = {}
    for param_name, param in sig.parameters.items():
        if param_name in additional_by_name:
            kwargs[param_name] = additional_by_name[param_name]
        elif param.annotation in additional_by_type:
            kwargs[param_name] = additional_by_type[param.annotation]
        elif param.annotation in configuration.injectable_dependencies_by_type:
            kwargs[param_name] = configuration.injectable_dependencies_by_type[
                param.annotation
            ]
        elif param_name in configuration.injectable_dependencies_by_name:
            kwargs[param_name] = configuration.injectable_dependencies_by_name[
                param_name
            ]
    return callable_(**kwargs)


class Configuration:
    def __init__(self):
        self.services: List[ServiceConfiguration] = []

        self.injectable_dependencies_by_type = {}
        self.injectable_dependencies_by_name = {}

        self._loaded_services = []
        self._cleanup = []

    async def finalize(self) -> None:
        for func in self._cleanup:
            await func()

    def register_injectable_dependency(
        self, value: Any, name: Optional[str] = None
    ) -> None:
        if name is not None:
            self.injectable_dependencies_by_name[name] = value
        self.injectable_dependencies_by_type[type(value)] = value

    async def initialize(self) -> None:
        pg_settings = PostgreSQLSettings()
        writer_db_pool = await asyncpg.create_pool(
            pg_settings.postgres_writer_dsn,
            min_size=1,
            max_size=pg_settings.postgres_pool_size,
        )
        self._cleanup.append(writer_db_pool.close)
        if pg_settings.postgres_reader_host is None:
            reader_db_pool = writer_db_pool
        else:
            reader_db_pool = await asyncpg.create_pool(
                pg_settings.postgres_reader_dsn,
                min_size=1,
                max_size=pg_settings.postgres_pool_size,
            )
            self._cleanup.append(reader_db_pool.close)
        self.register_injectable_dependency(reader_db_pool, "reader_db_pool")
        self.register_injectable_dependency(writer_db_pool, "writer_db_pool")
        self.register_injectable_dependency(pg_settings, "pg_settings")

        # make sure to load dependencies first...
        for service in self.services:
            for dep_service in [
                dep_service
                for dep_service in self.services
                if dep_service.service_id in service.dependencies
            ]:
                await self._init_service(dep_service)

            await self._init_service(service)

    async def _init_service(self, service: ServiceConfiguration) -> None:
        if service.service_id in self._loaded_services:
            return

        for repo_type in service.repositories:
            instance = call_injectable(
                repo_type, self, {"settings": service.settings, "service": service}
            )
            await instance.initialize()
            self._cleanup.append(instance.finalize)
            self.register_injectable_dependency(instance)
        self._loaded_services.append(service.service_id)

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
