# Business rules

## Dataset

- Customer identities, gender assignments, brands, and transactions
  are synthetic sample data.
- All monetary values are USD.
- Sample orders cover January through March 2026.
- The date dimension initially contains only dates used by the sample.

## Fact table

- One fact_order_item row represents one order item.
- Its primary key is (order_id, line_number).
- All lines of an order share its customer, date, location, and status.
- Dates represent order placement dates.
- location_id identifies the order's shipping city.

## Customer attributes

- Allowed gender values are male, female, and not-specified.
- Customer segments are Standard and Premium.

## Product attributes

- Each product has a name, category, and brand.
- Multiple products can share a brand.

## Location hierarchy

- Each dim_location row represents one city within a state and country.
- Multiple cities can belong to the same state.
- State totals group by country and state_name.
- City totals group by country, state_name, and city_name.

## Metrics

- Line sales = quantity * unit_price - discount_amount.
- discount_amount is the total discount for the entire line.
- Net sales includes only completed orders.
- Completed orders = distinct completed order IDs.
- Units sold = sum of quantities on completed orders.
- Average order value = net sales / completed orders.
- An empty period has zero net sales, orders, and units.
- Average order value is undefined when there are no completed orders.
- Default sales or revenue questions mean completed net sales.

## Initial scope

- Taxes, shipping charges, refunds, and currency conversion are excluded.

## Expected baseline

- 4 customers.
- 6 products.
- 6 shipping locations.
- 8 calendar dates.
- 16 order-item rows.
- 10 distinct orders.
- 8 completed orders.
- 2 cancelled orders.
- 22 units sold on completed orders.
- Completed net sales: 835.00 USD.
- Average order value: 104.38 USD.
- March completed net sales: 495.00 USD.