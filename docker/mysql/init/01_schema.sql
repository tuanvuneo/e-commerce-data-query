USE ecommerce_dw;


CREATE TABLE dim_customer (
    customer_id INT NOT NULL
        COMMENT 'Unique customer identifier',

    customer_name VARCHAR(100) NOT NULL
        COMMENT 'Fictional customer name',

    gender VARCHAR(20) NOT NULL DEFAULT 'not-specified'
        COMMENT 'Customer gender: male, female, or not-specified',

    customer_segment VARCHAR(20) NOT NULL
        COMMENT 'Customer segment: Standard or Premium',

    PRIMARY KEY (customer_id),

    CONSTRAINT chk_customer_gender
        CHECK (
            gender IN ('male', 'female', 'not-specified')
        )
) ENGINE=InnoDB
  COMMENT='Customer descriptions for the teaching dataset';


CREATE TABLE dim_product (
    product_id INT NOT NULL
        COMMENT 'Unique product identifier',

    product_name VARCHAR(100) NOT NULL
        COMMENT 'English product name',

    category VARCHAR(50) NOT NULL
        COMMENT 'Product category',

    brand VARCHAR(80) NOT NULL
        COMMENT 'Product brand name',

    PRIMARY KEY (product_id)
) ENGINE=InnoDB
  COMMENT='Product descriptions including category and brand';


CREATE TABLE dim_location (
    location_id INT NOT NULL
        COMMENT 'Unique shipping city identifier',

    city_name VARCHAR(100) NOT NULL
        COMMENT 'English name of the shipping city',

    state_name VARCHAR(100) NOT NULL
        COMMENT 'English name of the state containing the city',

    country VARCHAR(50) NOT NULL
        COMMENT 'English name of the country containing the state',

    PRIMARY KEY (location_id),

    UNIQUE KEY uq_location_country_state_city (
        country,
        state_name,
        city_name
    )
) ENGINE=InnoDB
  COMMENT='One row per shipping city within a state and country';


CREATE TABLE dim_date (
    date_id INT NOT NULL
        COMMENT 'Date identifier in YYYYMMDD format',

    full_date DATE NOT NULL
        COMMENT 'Calendar date used as the order placement date',

    calendar_year SMALLINT NOT NULL
        COMMENT 'Four-digit calendar year',

    month_number TINYINT NOT NULL
        COMMENT 'Calendar month number from 1 to 12',

    month_name VARCHAR(9) NOT NULL
        COMMENT 'English calendar month name',

    PRIMARY KEY (date_id),

    UNIQUE KEY uq_dim_date_full_date (full_date),

    CONSTRAINT chk_date_month
        CHECK (month_number BETWEEN 1 AND 12)
) ENGINE=InnoDB
  COMMENT='Calendar dates used by the teaching dataset';


CREATE TABLE fact_order_item (
    order_id VARCHAR(20) NOT NULL
        COMMENT 'Order identifier shared by all items in an order',

    line_number SMALLINT NOT NULL
        COMMENT 'Item line number within the order',

    date_id INT NOT NULL
        COMMENT 'Order placement date identifier',

    customer_id INT NOT NULL
        COMMENT 'Customer who placed the order',

    product_id INT NOT NULL
        COMMENT 'Product purchased on this line',

    location_id INT NOT NULL
        COMMENT 'Shipping city identifier for the order',

    quantity INT NOT NULL
        COMMENT 'Number of product units on this line',

    unit_price DECIMAL(10, 2) NOT NULL
        COMMENT 'Historical sale price per unit in USD',

    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00
        COMMENT 'Total discount for the entire line in USD',

    order_status VARCHAR(20) NOT NULL
        COMMENT 'Order status: completed or cancelled',

    PRIMARY KEY (order_id, line_number),

    CONSTRAINT fk_order_item_date
        FOREIGN KEY (date_id)
        REFERENCES dim_date (date_id),

    CONSTRAINT fk_order_item_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customer (customer_id),

    CONSTRAINT fk_order_item_product
        FOREIGN KEY (product_id)
        REFERENCES dim_product (product_id),

    CONSTRAINT fk_order_item_location
        FOREIGN KEY (location_id)
        REFERENCES dim_location (location_id),

    CONSTRAINT chk_order_item_line_number
        CHECK (line_number > 0),

    CONSTRAINT chk_order_item_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_order_item_unit_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_order_item_discount
        CHECK (
            discount_amount >= 0
            AND discount_amount <= quantity * unit_price
        ),

    CONSTRAINT chk_order_item_status
        CHECK (
            order_status IN ('completed', 'cancelled')
        )
) ENGINE=InnoDB
  COMMENT='One row per order item; monetary amounts are in USD';