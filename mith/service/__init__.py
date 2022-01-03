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

        for service in configuration.services:
            objects, schema = generate_graphql(configuration, service)

            mount_path = f"/{service.service_id}"
            self.mount(
                mount_path,
                ariadne.asgi.GraphQL(
                    make_federated_schema(schema, *objects, directives={}),
                    extensions=[ApolloTracingExtension],
                ),
            )
            print(f"Mounting {mount_path}")

        self.add_event_handler("startup", self.initialize)
        self.add_event_handler("shutdown", self.finalize)

    async def initialize(self) -> None:
        await self.configuration.initialize()

    async def finalize(self) -> None:
        await self.configuration.finalize()
