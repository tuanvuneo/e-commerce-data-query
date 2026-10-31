import asyncio
import json

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.catalog.models import (
    CatalogColumn,
    CatalogMetric,
    CatalogRelationship,
    CatalogTable,
)
from app.config import MetadataSettings
from app.database import create_metadata_engine


async def main() -> None:
    engine = create_metadata_engine(MetadataSettings())
    Session = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with Session() as session:
            models = {
                "tables": CatalogTable,
                "columns": CatalogColumn,
                "relationships": CatalogRelationship,
                "metrics": CatalogMetric,
            }

            counts = {}

            for name, model in models.items():
                counts[name] = await session.scalar(
                    select(func.count()).select_from(model)
                )

            expected_counts = {
                "tables": 5,
                "columns": 27,
                "relationships": 4,
                "metrics": 4,
            }

            if counts != expected_counts:
                raise AssertionError(
                    f"Expected {expected_counts}, received {counts}"
                )

            fact_table = await session.get(
                CatalogTable,
                "fact_order_item",
            )

            if (
                fact_table is None
                or fact_table.primary_key != ["order_id", "line_number"]
            ):
                raise AssertionError(
                    "The fact table primary key must preserve "
                    "the order: order_id, line_number."
                )

            metrics = (
                await session.scalars(select(CatalogMetric))
            ).all()

            expected_metric_names = {
                "net_sales",
                "completed_orders",
                "units_sold",
                "average_order_value",
            }

            if {metric.name for metric in metrics} != expected_metric_names:
                raise AssertionError("Unexpected metric names.")

            for metric in metrics:
                if metric.filters != {
                    "fact_order_item.order_status": "completed"
                }:
                    raise AssertionError(
                        f"Unexpected filters for {metric.name}"
                    )

        print(json.dumps(counts, indent=2))
        print(
            "Catalog counts, primary-key order, "
            "and metric filters passed."
        )

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())