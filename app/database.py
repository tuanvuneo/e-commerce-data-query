from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import Settings, MetadataSettings

def create_warehouse_engine(settings: Settings) -> AsyncEngine:

    url = URL.create(
        drivername="mysql+asyncmy",
        username=settings.mysql_reader_user,
        password=settings.mysql_reader_password.get_secret_value(),
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=settings.mysql_database,
        query={"charset": "utf8mb4"},
    )

    return create_async_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=0,
        pool_timeout=5,
        connect_args={"connect_timeout": 5},
    )

def create_metadata_engine(settings: MetadataSettings) -> AsyncEngine:
    if (
        settings.metadata_database.casefold()
        == settings.mysql_database.casefold()
    ):
        raise ValueError(
            "The metadata database must differ from the warehouse database."
        )

    url = URL.create(
        drivername="mysql+asyncmy",
        username=settings.metadata_writer_user,
        password=settings.metadata_writer_password.get_secret_value(),
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=settings.metadata_database,
        query={"charset": "utf8mb4"},
    )

    return create_async_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=0,
        pool_timeout=5,
        connect_args={"connect_timeout": 5},
    )