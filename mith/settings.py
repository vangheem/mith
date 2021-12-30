from pydantic import BaseSettings
from typing import Optional


class PostgreSQLSettings(BaseSettings):
    postgres_reader_host: Optional[str] = None
    postgres_writer_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_pool_size: int = 10

    @property
    def postgres_reader_dsn(self) -> str:
        return (
            f"postgres://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_reader_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_writer_dsn(self) -> str:
        return (
            f"postgres://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_writer_host}:{self.postgres_port}/{self.postgres_db}"
        )
