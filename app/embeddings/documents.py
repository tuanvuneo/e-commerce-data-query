from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.catalog.models import (
    CatalogColumn,
    CatalogMetric,
    CatalogTable,
)


@dataclass(frozen=True)
class CatalogDocument:
    document_id: str
    catalog_id: str
    kind: Literal["column", "metric"]
    text: str
    payload: dict[str, Any]


def make_column_document(
    column: CatalogColumn,
    table: CatalogTable,
) -> CatalogDocument:
    text = "\n".join(
        [
            f"Database column: {column.id}",
            f"Description: {column.description}",
            f"Aliases: {', '.join(column.aliases) or 'None'}",
            f"Data type: {column.data_type}",
            (
                "Curated values: "
                f"{', '.join(column.allowed_values) or 'None'}"
            ),
            f"Table: {table.name}. {table.description}",
            f"Row meaning: {table.grain}",
        ]
    )

    payload = {
        "table_name": column.table_name,
        "column_name": column.name,
        "description": column.description,
        "data_type": column.data_type,
        "nullable": column.nullable,
        "ordinal_position": column.ordinal_position,
        "is_primary_key": column.is_primary_key,
        "aliases": list(column.aliases),
        "allowed_values": list(column.allowed_values),
        "source_database": table.source_database,
        "table_description": table.description,
        "table_grain": table.grain,
        "table_primary_key": list(table.primary_key),
    }

    return CatalogDocument(
        document_id=f"column:{column.id}",
        catalog_id=column.id,
        kind="column",
        text=text,
        payload=payload,
    )


def make_metric_document(
    metric: CatalogMetric,
    table: CatalogTable,
) -> CatalogDocument:
    filter_text = "; ".join(
        f"{column_id} = {value!r}"
        for column_id, value in sorted(metric.filters.items())
    )

    text = "\n".join(
        [
            f"Business metric: {metric.name}",
            f"Description: {metric.description}",
            f"Aliases: {', '.join(metric.aliases) or 'None'}",
            f"Unit: {metric.unit}",
            f"Required filters: {filter_text or 'None'}",
            (
                "Referenced columns: "
                f"{', '.join(metric.referenced_columns)}"
            ),
            f"SQL definition: {metric.sql_expression}",
            f"Base table: {table.name}. {table.description}",
            f"Row meaning: {table.grain}",
        ]
    )

    payload = {
        "name": metric.name,
        "base_table": metric.base_table,
        "description": metric.description,
        "unit": metric.unit,
        "sql_expression": metric.sql_expression,
        "filters": dict(metric.filters),
        "referenced_columns": list(metric.referenced_columns),
        "aliases": list(metric.aliases),
        "source_database": table.source_database,
        "table_description": table.description,
        "table_grain": table.grain,
        "table_primary_key": list(table.primary_key),
    }

    return CatalogDocument(
        document_id=f"metric:{metric.name}",
        catalog_id=metric.name,
        kind="metric",
        text=text,
        payload=payload,
    )


async def load_catalog_documents(
    engine: AsyncEngine,
) -> list[CatalogDocument]:
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        table_rows = (
            await session.scalars(
                select(CatalogTable).order_by(CatalogTable.name)
            )
        ).all()

        tables = {table.name: table for table in table_rows}

        columns = (
            await session.scalars(
                select(CatalogColumn).order_by(
                    CatalogColumn.table_name,
                    CatalogColumn.ordinal_position,
                )
            )
        ).all()

        metrics = (
            await session.scalars(
                select(CatalogMetric).order_by(CatalogMetric.name)
            )
        ).all()

        if not tables or not columns or not metrics:
            raise ValueError(
                "The catalog is empty or incomplete. "
                "Run uv run python -m app.build_catalog first."
            )

        documents = [
            make_column_document(column, tables[column.table_name])
            for column in columns
        ]

        documents.extend(
            make_metric_document(metric, tables[metric.base_table])
            for metric in metrics
        )

        return documents