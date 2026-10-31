USE ecommerce_dw;

START TRANSACTION;


INSERT INTO dim_customer (
    customer_id,
    customer_name,
    gender,
    customer_segment
)
VALUES
    (1, 'Alex Morgan', 'male', 'Premium'),
    (2, 'Jamie Lee', 'female', 'Standard'),
    (3, 'Taylor Reed', 'female', 'Premium'),
    (4, 'Jordan Blake', 'not-specified', 'Standard');


INSERT INTO dim_product (
    product_id,
    product_name,
    category,
    brand
)
VALUES
    (1, 'Wireless Mouse', 'Electronics', 'TechNova'),
    (2, 'Mechanical Keyboard', 'Electronics', 'TechNova'),
    (3, 'USB-C Hub', 'Electronics', 'ConnectPro'),
    (4, 'Cotton T-Shirt', 'Clothing', 'UrbanWear'),
    (5, 'Running Shoes', 'Footwear', 'Stride'),
    (6, 'Ceramic Mug', 'Home', 'HomeCraft');


INSERT INTO dim_location (
    location_id,
    city_name,
    state_name,
    country
)
VALUES
    (1, 'Chicago', 'Illinois', 'United States'),
    (2, 'Austin', 'Texas', 'United States'),
    (3, 'New York City', 'New York', 'United States'),
    (4, 'Los Angeles', 'California', 'United States'),
    (5, 'Dallas', 'Texas', 'United States'),
    (6, 'San Francisco', 'California', 'United States');


INSERT INTO dim_date (
    date_id,
    full_date,
    calendar_year,
    month_number,
    month_name
)
VALUES
    (20260105, '2026-01-05', 2026, 1, 'January'),
    (20260112, '2026-01-12', 2026, 1, 'January'),
    (20260203, '2026-02-03', 2026, 2, 'February'),
    (20260214, '2026-02-14', 2026, 2, 'February'),
    (20260303, '2026-03-03', 2026, 3, 'March'),
    (20260310, '2026-03-10', 2026, 3, 'March'),
    (20260320, '2026-03-20', 2026, 3, 'March'),
    (20260325, '2026-03-25', 2026, 3, 'March');


INSERT INTO fact_order_item (
    order_id,
    line_number,
    date_id,
    customer_id,
    product_id,
    location_id,
    quantity,
    unit_price,
    discount_amount,
    order_status
)
VALUES
    ('O1001', 1, 20260105, 1, 1, 1, 2, 25.00, 0.00, 'completed'),
    ('O1001', 2, 20260105, 1, 2, 1, 1, 80.00, 10.00, 'completed'),

    ('O1002', 1, 20260112, 2, 4, 2, 3, 20.00, 0.00, 'completed'),

    ('O1003', 1, 20260203, 3, 3, 3, 1, 50.00, 0.00, 'completed'),
    ('O1003', 2, 20260203, 3, 6, 3, 2, 15.00, 0.00, 'completed'),

    ('O1004', 1, 20260214, 4, 5, 4, 1, 100.00, 0.00, 'cancelled'),

    ('O1005', 1, 20260214, 1, 2, 1, 1, 80.00, 0.00, 'completed'),

    ('O1006', 1, 20260303, 2, 5, 5, 1, 100.00, 10.00, 'completed'),
    ('O1006', 2, 20260303, 2, 4, 5, 2, 20.00, 0.00, 'completed'),

    ('O1007', 1, 20260310, 3, 1, 3, 1, 25.00, 0.00, 'completed'),
    ('O1007', 2, 20260310, 3, 3, 3, 2, 50.00, 0.00, 'completed'),

    ('O1008', 1, 20260320, 4, 6, 6, 4, 15.00, 0.00, 'completed'),

    ('O1009', 1, 20260325, 1, 5, 1, 1, 100.00, 0.00, 'completed'),
    ('O1009', 2, 20260325, 1, 2, 1, 1, 80.00, 0.00, 'completed'),

    ('O1010', 1, 20260325, 2, 1, 2, 2, 25.00, 0.00, 'cancelled'),
    ('O1010', 2, 20260325, 2, 4, 2, 1, 20.00, 0.00, 'cancelled');


COMMIT;