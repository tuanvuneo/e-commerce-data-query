from typing import Any

from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine


def _inspect_schema(connection: Connection) -> dict[str, dict[str, Any]]:
    inspector = inspect(connection)
    tables = {}

    for table_name in sorted(inspector.get_table_names()):
        columns = []

        for position, column in enumerate(
            inspector.get_columns(table_name),
            start=1,
        ):
            columns.append(
                {
                    "name": column["name"],
                    "data_type": str(column["type"]),
                    "nullable": column["nullable"],
                    "ordinal_position": position,
                    "description": column.get("comment") or "",
                }
            )

        primary_key = inspector.get_pk_constraint(table_name)

        tables[table_name] = {
            "columns": columns,
            "primary_key": primary_key["constrained_columns"] or [],
            "foreign_keys": inspector.get_foreign_keys(table_name),
        }

    return tables


async def read_warehouse_schema(
    engine: AsyncEngine,
) -> dict[str, dict[str, Any]]:
    async with engine.connect() as connection:
        return await connection.run_sync(_inspect_schema)