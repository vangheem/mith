import os
from typing import Tuple, Any
from polymith.config import Configuration


def generate_graphql(configuration: Configuration) -> Tuple[Any, str]:

    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "shared.gql")
    ) as fi:
        schema = f"# SHARED GQL\n\n{fi.read()}\n\n"

    objects = []

    types = ""
    queries = ""
    mutations = ""

    breakpoint()
    for service in configuration.services:
        for api in service.apis:
            service_types = ""
            if service_types:
                types += (
                    f"# Generated {service.service_id} Types\n\n{service_types}\n\n"
                )
            service_queries = ""
            if service_queries:
                queries += (
                    f"# Generated {service.service_id} Queries\n\n{service_queries}\n\n"
                )
            service_mutations = ""
            if service_mutations:
                queries += f"# Generated {service.service_id} Mutations\n\n{service_mutations}\n\n"

    schema += types

    if not queries:
        # need to have something
        queries += "_: String"

    schema += f"type Query {{\n{queries}\n}}"

    if mutations:
        mutations += f"type Mutation {{\n{mutations}\n}}"

    print(schema)

    return objects, schema
