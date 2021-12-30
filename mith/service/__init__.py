import os
from typing import List

import ariadne
import ariadne.asgi
from ariadne.contrib.federation import make_federated_schema
from ariadne.contrib.tracing.apollotracing import ApolloTracingExtension
from fastapi import FastAPI

from mith.config import Configuration

from ..gql import generate_graphql


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
