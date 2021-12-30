from mith.config import Configuration

from .service import GraphQLApplication


def create_app(config: Configuration) -> GraphQLApplication:
    app = GraphQLApplication(config)
    return app
