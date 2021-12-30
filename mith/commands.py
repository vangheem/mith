from typing import Optional
from mith.settings import HTTPSettings
import dotenv
import typer
import uvicorn

from mith.app import create_app
from mith.config import load_configuration_from_environment

main = typer.Typer()


def _init_env(env_file: Optional[str] = None) -> None:
    if env_file is not None:
        dotenv.load_dotenv(env_file)


@main.command()
def run(env: Optional[str] = None):
    _init_env(env)
    config = load_configuration_from_environment()
    app = create_app(config)
    http_settings = HTTPSettings()
    return uvicorn.run(app, host=http_settings.host, port=http_settings.port)


@main.command()
def run_service(name: str, env: Optional[str] = None):
    _init_env(env)
    print(f"Run {name}")


@main.command()
def build_graphql(env: Optional[str] = None):
    _init_env(env)
    print("Build graphql")


if __name__ == "__main__":
    main()
