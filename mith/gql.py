import os
from typing import List, Tuple, Dict, Annotated, Type, Any
from pydantic.main import BaseModel

from mith.config import APIDefinition, Configuration
from ariadne.contrib import federation


def _issubclass(type_: Any, sub: Any) -> bool:
    try:
        return issubclass(type_, sub)
    except TypeError:
        return False


def _find_pydantic_types(type_: Annotated) -> List[Type[BaseModel]]:
    if _issubclass(type_, BaseModel):
        return [type_]

    result = []
    [
        result.extend(_find_pydantic_types(subtype))
        for subtype in getattr(type_, "__args__", [])
    ]
    return result


def generate_gql_type_signature(type_: Any) -> str:
    if issubclass(type_, BaseModel):
        return type_.__name__

    if type_ == str:
        return "String"
    if type_ == int:
        return "Integer"
    else:
        raise Exception(f"Unsupported type: {type_}")


def generate_api_gql_types(
    api: APIDefinition,
) -> Dict[str, federation.FederatedObjectType]:
    result = {}

    for func_name in dir(api.contract):
        func = getattr(api.contract, func_name)
        if (
            func_name.startswith("_")
            or not callable(func)
            or not hasattr(func, "__mith__")
        ):
            continue

        for type_ in func.__annotations__.values():
            for found_type in _find_pydantic_types(type_):
                breakpoint()
                type_def = ""
                result[found_type.__name__] = type_def

    return result


class TypeConflictError(Exception):
    ...


def generate_graphql(
    configuration: Configuration,
) -> Tuple[List[federation.FederatedObjectType], str]:

    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "shared.gql")
    ) as fi:
        schema = f"# SHARED GQL\n\n{fi.read()}\n\n"

    objects = {
        "query": federation.FederatedObjectType("Query"),
    }

    types = {}
    queries = []
    mutations = []

    for service in configuration.services:
        for api in service.apis:
            objects_types = generate_api_gql_types(api)
            if len(objects_types) > 0:
                service_types = []
                for type_name, type_def in objects_types.items():
                    if type_name in objects:
                        if types[type_name] != type_def:
                            raise TypeConflictError(
                                f"Type names must to be unique:\n{types[type_name]} != {type_def}"
                            )
                        continue
                    types[type_name] = type_def
                objects[type_name] = federation.FederatedObjectType(type_name)

            # service_queries = ""
            # if service_queries:
            #     queries += (
            #         f"# Generated {service.service_id} Queries\n\n{service_queries}\n\n"
            #     )
            # service_mutations = ""
            # if service_mutations:
            #     queries += f"# Generated {service.service_id} Mutations\n\n{service_mutations}\n\n"

    for type_name, type_def in types.items():
        schema += f"# Generated Type\n\n{type_name}\n\n{type_def}"

    if len(queries) == 0:
        # need to have something
        queries.append("_: String")

    query_str = "\n".join(queries)
    schema += f"""type Query {{
{query_str}
}}"""

    if mutations:
        objects["mutation"] = federation.FederatedObjectType("Mutation")
        mutations_str = "\n".join(mutations)
        mutations += f"""type Mutation {{
{mutations_str}
}}"""

    print(schema)

    return list(objects.values()), schema
