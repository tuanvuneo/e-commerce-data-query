from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.catalog.config import CatalogConfig, ColumnConfig
from app.catalog.models import (
    CatalogBase,
    CatalogColumn,
    CatalogMetric,
    CatalogRelationship,
    CatalogTable,
)
from app.catalog.schema import read_warehouse_schema


def validate_catalog(
    config: CatalogConfig,
    schema: dict[str, dict[str, Any]],
    source_database: str,
) -> None:
    configured_tables = set(config.tables)
    actual_tables = set(schema)

    if configured_tables != actual_tables:
        missing = sorted(configured_tables - actual_tables)
        unexpected = sorted(actual_tables - configured_tables)

        raise ValueError(
            f"Table mismatch. Missing: {missing}. Unexpected: {unexpected}."
        )

    column_ids = {
        f"{table_name}.{column['name']}"
        for table_name, table in schema.items()
        for column in table["columns"]
    }

    unknown_overrides = set(config.columns) - column_ids

    if unknown_overrides:
        raise ValueError(
            f"Unknown configured columns: {sorted(unknown_overrides)}"
        )

    for table_name, table in schema.items():
        if not table["primary_key"]:
            raise ValueError(f"Table has no primary key: {table_name}")

        for column in table["columns"]:
            column_id = f"{table_name}.{column['name']}"
            override = config.columns.get(column_id, ColumnConfig())
            description = override.description or column["description"]

            if not description.strip():
                raise ValueError(
                    f"Add an English description for {column_id}"
                )

        for foreign_key in table["foreign_keys"]:
            if not foreign_key.get("name"):
                raise ValueError(
                    f"Foreign key needs a name in {table_name}"
                )

            target_database = foreign_key.get("referred_schema")

            if target_database not in (None, source_database):
                raise ValueError(
                    "This catalog supports relationships within "
                    f"{source_database} only."
                )

            source_columns = foreign_key["constrained_columns"]
            target_columns = foreign_key["referred_columns"]
            target_table = foreign_key["referred_table"]

            if not source_columns or len(source_columns) != len(target_columns):
                raise ValueError(
                    f"Invalid foreign key: {foreign_key['name']}"
                )

            for source_column, target_column in zip(
                source_columns,
                target_columns,
                strict=True,
            ):
                references = {
                    f"{table_name}.{source_column}",
                    f"{target_table}.{target_column}",
                }

                if not references <= column_ids:
                    raise ValueError(
                        f"Unknown foreign-key columns: {sorted(references)}"
                    )

    for metric_name, metric in config.metrics.items():
        if metric.base_table not in actual_tables:
            raise ValueError(
                f"Unknown base table for metric {metric_name}"
            )

        references = set(metric.referenced_columns) | set(metric.filters)
        unknown_references = references - column_ids

        if unknown_references:
            raise ValueError(
                f"Unknown columns in metric {metric_name}: "
                f"{sorted(unknown_references)}"
            )


async def rebuild_catalog(
    warehouse_engine: AsyncEngine,
    metadata_engine: AsyncEngine,
    config: CatalogConfig,
    source_database: str,
) -> dict[str, int]:
    schema = await read_warehouse_schema(warehouse_engine)

    validate_catalog(config, schema, source_database)

    async with metadata_engine.begin() as connection:
        await connection.run_sync(CatalogBase.metadata.create_all)

    Session = async_sessionmaker(
        metadata_engine,
        expire_on_commit=False,
    )

    async with Session.begin() as session:
        # Delete children before their parent table records.
        for model in (
            CatalogRelationship,
            CatalogMetric,
            CatalogColumn,
            CatalogTable,
        ):
            await session.execute(delete(model))

        for table_name, table in schema.items():
            table_config = config.tables[table_name]

            session.add(
                CatalogTable(
                    name=table_name,
                    source_database=source_database,
                    role=table_config.role,
                    grain=table_config.grain,
                    description=table_config.description,
                    primary_key=table["primary_key"],
                )
            )

        # Insert parent records before records that reference them.
        await session.flush()

        for table_name, table in schema.items():
            for column in table["columns"]:
                column_id = f"{table_name}.{column['name']}"
                override = config.columns.get(column_id, ColumnConfig())

                session.add(
                    CatalogColumn(
                        id=column_id,
                        table_name=table_name,
                        name=column["name"],
                        data_type=column["data_type"],
                        nullable=column["nullable"],
                        ordinal_position=column["ordinal_position"],
                        is_primary_key=(
                            column["name"] in table["primary_key"]
                        ),
                        description=(
                            override.description or column["description"]
                        ),
                        aliases=override.aliases,
                        allowed_values=override.allowed_values,
                    )
                )

            for foreign_key in table["foreign_keys"]:
                session.add(
                    CatalogRelationship(
                        id=f"{table_name}.{foreign_key['name']}",
                        name=foreign_key["name"],
                        source_table=table_name,
                        target_table=foreign_key["referred_table"],
                        source_columns=foreign_key["constrained_columns"],
                        target_columns=foreign_key["referred_columns"],
                    )
                )

        for metric_name, metric in config.metrics.items():
            session.add(
                CatalogMetric(
                    name=metric_name,
                    **metric.model_dump(),
                )
            )

    return {
        "tables": len(schema),
        "columns": sum(len(table["columns"]) for table in schema.values()),
        "relationships": sum(
            len(table["foreign_keys"]) for table in schema.values()
        ),
        "metrics": len(config.metrics),
    }