from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

def _validate_period(start_date: date, end_date: date) -> None:
    if start_date >= end_date:
        raise ValueError('start_date must be earlier than end_date')

class WarehouseRepository: 
    def __init__(self, connection: AsyncConnection) -> None:
        self.connection = connection
    
    async def get_database_info(self) -> dict[str, object]:
        statement = text(
            """
            SELECT
                DATABASE() AS database_name,
                CURRENT_USER() AS account,
                VERSION() AS version
            """
        )

        result = await self.connection.execute(statement)

        return dict(result.mappings().one())

    async def get_sales_summary(
        self,
        start_date: date,
        end_date: date,
    ) -> dict[str, object]:
        """Read completed sales within [start_date, end_date)."""
        _validate_period(start_date, end_date)

        statement = text(
            """
            SELECT
                COALESCE(
                    SUM(f.quantity * f.unit_price - f.discount_amount),
                    0.00
                ) AS net_sales,
                COUNT(DISTINCT f.order_id) AS completed_orders,
                COALESCE(SUM(f.quantity), 0) AS units_sold,
                ROUND(
                    SUM(f.quantity * f.unit_price - f.discount_amount)
                    / NULLIF(COUNT(DISTINCT f.order_id), 0),
                    2
                ) AS average_order_value
            FROM fact_order_item AS f
            JOIN dim_date AS d
                ON f.date_id = d.date_id
            WHERE f.order_status = :status
                AND d.full_date >= :start_date
                AND d.full_date < :end_date
            """
        )

        result = await self.connection.execute(
            statement,
            {
                "status": "completed",
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        row = result.mappings().one()

        return {
            "net_sales": row["net_sales"],
            "completed_orders": int(row["completed_orders"]),
            "units_sold": int(row["units_sold"]),
            "average_order_value": row["average_order_value"],
        }

    async def get_sales_by_state(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, object]]:
        """Combine completed sales from cities within each state."""
        _validate_period(start_date, end_date)

        statement = text(
            """
            SELECT
                l.country,
                l.state_name,
                SUM(
                    f.quantity * f.unit_price - f.discount_amount
                ) AS net_sales,
                COUNT(DISTINCT f.order_id) AS completed_orders
            FROM fact_order_item AS f
            JOIN dim_location AS l
                ON f.location_id = l.location_id
            JOIN dim_date AS d
                ON f.date_id = d.date_id
            WHERE f.order_status = :status
                AND d.full_date >= :start_date
                AND d.full_date < :end_date
            GROUP BY
                l.country,
                l.state_name
            ORDER BY
                net_sales DESC,
                l.state_name
            """
        )

        result = await self.connection.execute(
            statement,
            {
                "status": "completed",
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        return [dict(row) for row in result.mappings().all()]
