import asyncio
import json

from app.catalog.config import CatalogConfig
from app.catalog.service import rebuild_catalog
from app.config import PROJECT_ROOT, MetadataSettings
from app.database import create_metadata_engine, create_warehouse_engine


async def main() -> None:
    settings = MetadataSettings()

    config_path = PROJECT_ROOT / "config" / "catalog.json"
    config = CatalogConfig.model_validate_json(
        config_path.read_text(encoding="utf-8")
    )

    warehouse_engine = create_warehouse_engine(settings)
    metadata_engine = create_metadata_engine(settings)

    try:
        counts = await rebuild_catalog(
            warehouse_engine=warehouse_engine,
            metadata_engine=metadata_engine,
            config=config,
            source_database=settings.mysql_database,
        )

        print(json.dumps(counts, indent=2))
    finally:
        await metadata_engine.dispose()
        await warehouse_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())