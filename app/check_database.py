import asyncio
import json
from datetime import date
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.config import Settings
from app.database import create_warehouse_engine
from app.repositories.warehouse import WarehouseRepository


async def main() -> None:
    settings = Settings()
    engine = create_warehouse_engine(settings)

    try:
        async with engine.connect() as connection:
            repository = WarehouseRepository(connection)

            info = await repository.get_database_info()

            print("Database:", info["database_name"])
            print("Account:", info["account"])

            summary = await repository.get_sales_summary(
                date(2026, 1, 1),
                date(2026, 4, 1),
            )

            march = await repository.get_sales_summary(
                date(2026, 3, 1),
                date(2026, 4, 1),
            )

            empty = await repository.get_sales_summary(
                date(2026, 4, 1),
                date(2026, 5, 1),
            )

            states = await repository.get_sales_by_state(
                date(2026, 1, 1),
                date(2026, 4, 1),
            )

        expected_summary = {
            "net_sales": Decimal("835.00"),
            "completed_orders": 8,
            "units_sold": 22,
            "average_order_value": Decimal("104.38"),
        }

        assert summary == expected_summary, summary
        assert isinstance(summary["net_sales"], Decimal)

        assert march["net_sales"] == Decimal("495.00"), march
        assert march["completed_orders"] == 4, march

        assert empty == {
            "net_sales": Decimal("0.00"),
            "completed_orders": 0,
            "units_sold": 0,
            "average_order_value": None,
        }, empty

        expected_state_sales = {
            "Illinois": Decimal("380.00"),
            "New York": Decimal("205.00"),
            "Texas": Decimal("190.00"),
            "California": Decimal("60.00"),
        }

        actual_state_sales = {
            row["state_name"]: row["net_sales"]
            for row in states
        }

        assert len(states) == 4, states
        assert actual_state_sales == expected_state_sales, states

        async with engine.connect() as connection:
            try:
                await connection.execute(
                    text(
                        """
                        UPDATE dim_product
                        SET product_name = product_name
                        WHERE 1 = 0
                        """
                    )
                )
            except DBAPIError as exc:
                if exc.orig.args[0] != 1142:
                    raise
            else:
                raise RuntimeError(
                    "The reader account can UPDATE. Check its grants."
                )

        print("Reader UPDATE check: denied (expected).")
        print("All sample dates:")
        print(json.dumps(summary, default=str, indent=2))

        print("Sales by state:")
        for row in states:
            print(row["state_name"], row["net_sales"])

        print("March net sales:", march["net_sales"])
        print("Empty-period checks passed.")
        print("All database checks passed.")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())