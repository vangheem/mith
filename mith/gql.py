import itertools
import logging
import os
import typing

from ariadne.contrib import federation
import pydantic
from pydantic.main import BaseModel

from mith.config import (
    APIDefinition,
    Configuration,
    ServiceConfiguration,
    call_injectable,
)

from .const import EndpointType

logger = logging.getLogger(__name__)


class TypeConflictError(Exception):
    ...


class InvalidQuery(Exception):
    ...


def _issubclass(type_: typing.Any, sub: typing.Any) -> bool:
    try:
        return issubclass(type_, sub)
    except TypeError:
        return False


def _find_pydantic_types(
    type_: typing.Annotated,
) -> typing.List[typing.Type[BaseModel]]:
    if _issubclass(type_, BaseModel):
        return [type_] + list(
            itertools.chain(
                *[
                    _find_pydantic_types(field.type_)
                    for field in type_.__fields__.values()
                ]
            )
        )

    return list(
        itertools.chain(
            *[
                _find_pydantic_types(subtype)
                for subtype in getattr(type_, "__args__", [])
            ]
        )
    )


def _generate_gql_type_signature(type_: typing.Any) -> str:
    if _issubclass(type_, BaseModel):
        return type_.__name__

    if type_ == str:
        return "String"
    elif type_ == int:
        return "Integer"
    elif type_ == float:
        return "Float"
    elif type_ == float:
        return "Boolean"
    elif type_ is None:
        return ""
    elif typing.get_origin(type_) == list:
        return "[" + generate_gql_type_signature(type_.__args__[0]) + "]"
    else:
        raise Exception(f"Unsupported type: {type_}")


def generate_gql_type_signature(type_: typing.Any) -> str:
    if type_ is None:
        return ""

    trailing = "!"
    if typing.get_origin(type_) is typing.Union:
        aargs = typing.get_args(type_)
        if len(aargs) == 2 and aargs[1] == type(None):
            trailing = ""
            type_ = aargs[0]
    return _generate_gql_type_signature(type_) + trailing


def generate_gql_type_from_pydantic(type_: typing.Type[BaseModel]) -> str:
    fields = []
    primary_keys = []
    reference = getattr(type_.__config__, "reference", False)
    for f_name, field in type_.__fields__.items():
        type_sig = type_.__annotations__[f_name]
        f_str = f"{f_name}: {generate_gql_type_signature(type_sig)}"

        if field.field_info.extra.get("primary_key"):
            primary_keys.append(f_name)
            if reference:
                f_str += " @external"

        fields.append(f_str)

    fields_str = "\n  ".join(fields)

    extra_str = ""
    if len(primary_keys) > 0:
        extra_str = f'@key(fields: "{" ".join(primary_keys)}")'

    if reference:
        extra_str += f" @extends"

    return f"""type {type_.__name__} {extra_str} {{
  {fields_str}
}}"""


class APIEndpiont:
    def __init__(self, func, api: APIDefinition, configuration: Configuration):
        self.func = func
        self.api = api
        self.configuration = configuration

    @property
    def name(self) -> str:
        return self.func.__mith__["name"]

    @property
    def type(self) -> str:
        return self.func.__mith__["type"]

    @property
    def arguments(self) -> typing.Dict[str, typing.Any]:
        values = self.func.__annotations__.copy()
        values.pop("return", None)
        return values

    @property
    def model_type(self) -> typing.Type[pydantic.BaseModel]:
        return self.func.__mith__["model_type"]

    @property
    def returns(self) -> typing.Any:
        return self.func.__annotations__.get("return")

    def __repr__(self):
        return f"<APIEndpiont {self.name}, func: {self.func} />"

    async def __call__(self, context, *args, **kwargs) -> typing.Any:
        api = self.api.implementor()
        impl = getattr(api, self.func.__name__)
        return await call_injectable(
            impl, self.configuration, {"context": context, **kwargs}
        )

    async def reference_resolver(self, _, context, representation) -> typing.Any:
        result = await self(context, **representation)
        if result is not None and isinstance(result, BaseModel):
            data = result.dict()
            data["__typename"] = self.model_type.__name__
            return data
        return result


class _GraphQLGenerator:
    def __init__(self, configuration: Configuration, service: ServiceConfiguration):
        self.configuration = configuration
        self.service = service
        self.objects = {
            "query": federation.FederatedObjectType("Query"),
        }

    def __call__(
        self,
    ) -> typing.Tuple[typing.List[federation.FederatedObjectType], str]:
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "shared.gql")
        ) as fi:
            schema = f"# SHARED GQL\n\n{fi.read()}\n\n"

        types = {}
        queries = []
        mutations = []
        mutation_object = federation.FederatedObjectType("Mutation")

        for api in self.service.apis:
            objects_types = self.generate_api_gql_types(api)
            if len(objects_types) > 0:
                for type_name, type_def in objects_types.items():
                    if type_name in self.objects:
                        if types[type_name] != type_def:
                            raise TypeConflictError(
                                f"Type names must to be unique:\n{types[type_name]} != {type_def}"
                            )
                        continue
                    types[type_name] = type_def
                self.objects[type_name] = federation.FederatedObjectType(type_name)

            queries.extend(self.generate_api_queries(api, self.objects["query"]))
            mutations.extend(self.generate_api_mutations(api, mutation_object))
            self.wire_resolvers(api)

        for type_name, type_def in types.items():
            schema += f"# Generated Type: {type_name}\n{type_def}\n"

        if len(queries) == 0:
            # need to have something
            queries.append("_: String")

        query_str = "\n  ".join(queries)
        schema += f"""type Query {{
  {query_str}
}}

    """

        if mutations:
            self.objects["mutation"] = mutation_object
            mutations_str = "\n  ".join(mutations)
            schema += f"""type Mutation {{
  {mutations_str}
}}

    """

        logger.debug(schema)
        print(f"Schema {self.service.service_id}:\n {schema}")

        return list(self.objects.values()), schema

    def iter_api_contract(
        self, api: APIDefinition
    ) -> typing.Generator[APIEndpiont, None, None]:
        for func_name in dir(api.contract):
            func = getattr(api.contract, func_name)
            if (
                func_name.startswith("_")
                or not callable(func)
                or not hasattr(func, "__mith__")
            ):
                continue

            yield APIEndpiont(func, api, self.configuration)

    def generate_api_gql_types(
        self, api: APIDefinition
    ) -> typing.Dict[str, federation.FederatedObjectType]:
        result = {}

        for endpoint in self.iter_api_contract(api):
            for type_ in list(endpoint.arguments.values()) + [endpoint.returns]:
                for found_type in _find_pydantic_types(type_):
                    result[found_type.__name__] = generate_gql_type_from_pydantic(
                        found_type
                    )

        return result

    def generate_api_query(self, endpoint: APIEndpiont) -> str:
        aargs = []
        for name, type_def in endpoint.arguments.items():
            aargs.append(f"{name}: {generate_gql_type_signature(type_def)}")

        query = endpoint.name
        if len(aargs) > 0:
            query += f'({", ".join(aargs)})'
        if endpoint.returns is not None:
            query += f": {generate_gql_type_signature(endpoint.returns)}"

        return query

    def generate_api_queries(
        self, api: APIDefinition, query_object: federation.FederatedObjectType
    ) -> typing.List[str]:
        queries = []
        for endpoint in self.iter_api_contract(api):
            if endpoint.type != EndpointType.QUERY:
                continue
            if endpoint.returns is None:
                raise InvalidQuery(f"Query must have a return type: {endpoint}")
            queries.append(self.generate_api_query(endpoint))
            query_object.field(endpoint.name)(endpoint)
        return queries

    def generate_api_mutations(
        self, api: APIDefinition, mutation_object: federation.FederatedObjectType
    ) -> typing.List[str]:
        queries = []
        for endpoint in self.iter_api_contract(api):
            if endpoint.type != EndpointType.MUTATION:
                continue
            if endpoint.returns is None:
                raise InvalidQuery(f"Query must have a return type: {endpoint}")
            queries.append(self.generate_api_query(endpoint))
            mutation_object.field(endpoint.name)(endpoint)
        return queries

    def wire_resolvers(self, api: APIDefinition) -> typing.List[str]:
        queries = []
        for endpoint in self.iter_api_contract(api):
            if endpoint.type != EndpointType.RESOLVE_REFERENCE:
                continue

            self.objects[endpoint.model_type.__name__].reference_resolver(
                endpoint.reference_resolver
            )
        return queries


def generate_graphql(
    configuration: Configuration, service: ServiceConfiguration
) -> typing.Tuple[typing.List[federation.FederatedObjectType], str]:
    gen = _GraphQLGenerator(configuration, service)
    return gen()
