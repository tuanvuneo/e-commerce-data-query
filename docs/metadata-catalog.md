# Metadata catalog

The ecommerce_meta database describes the ecommerce_dw warehouse.

It contains:
- catalog_table: table descriptions, roles, grains, and ordered primary keys.
- catalog_column: column structure, descriptions, aliases, and curated values.
- catalog_relationship: foreign-key relationships with ordered column pairs.
- catalog_metric: metric descriptions, SQL expressions, filters, and references.

Build:
uv run python -m app.build_catalog

Check:
uv run python -m app.check_catalog

Expected counts:
5 tables, 27 columns, 4 relationships, and 4 metrics.

Descriptions and aliases are maintained in config/catalog.json.
Column descriptions fall back to warehouse SQL comments.

Each build replaces rows in the four catalog tables.
Metric expressions use f as the fact_order_item alias.
Metric filters must be applied when constructing queries.

Default sales metrics include completed orders.
Customer gender values are male, female, and not-specified.
Locations represent cities within states and countries.
State totals group by country and state_name.