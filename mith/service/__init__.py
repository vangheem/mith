from fastapi import FastAPI
import os

from polymith.config import Configuration
import ariadne
from ariadne.contrib.federation import make_federated_schema
from ariadne.contrib.tracing.apollotracing import ApolloTracingExtension
import ariadne.asgi
from ..gql import generate_graphql
from typing import List


class GraphQLApplication(FastAPI):
    def __init__(self, configuration: Configuration, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configuration = configuration

        objects, schema = generate_graphql(configuration)

        self.mount(
            "/graphql",
            ariadne.asgi.GraphQL(
                make_federated_schema(schema, *objects, directives={}),
                extensions=[ApolloTracingExtension],
            ),
        )
