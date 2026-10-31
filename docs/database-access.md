# Database access

## Warehouse

- Database: ecommerce_dw
- Python connects through the published host port.
- Default host: 127.0.0.1
- Default published port: 3307

## Accounts

- root is used for initialization and administration.
- ecommerce_reader is used by Python for warehouse reads.
- The intended reader grant is SELECT on ecommerce_dw.*.
- Real passwords are stored in the private environment file.

## Python structure

- Settings loads and validates database configuration.
- create_warehouse_engine constructs the engine and connection pool.
- WarehouseRepository contains warehouse queries.
- Each operation borrows a connection with async with.
- The application disposes of its engine during shutdown.

## Date ranges

- start_date is inclusive.
- end_date is exclusive.
- start_date must be earlier than end_date.

## Verification

Run:

`uv run python -m app.check_database`

Expected baseline:

- Completed net sales: 835.00 USD
- Completed orders: 8
- Units sold: 22
- Average order value: 104.38 USD
- March completed net sales: 495.00 USD
- Texas completed net sales across all sample dates: 190.00 USD

## Health endpoints

- /health checks whether the API responds.
- /health/db checks database connectivity and a simple query.

## Rebuilding the database

Recreating an empty database volume removes previously created accounts.
Provision ecommerce_reader again before running Python database checks.