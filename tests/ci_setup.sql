DROP TABLE IF EXISTS order_reviews, order_payments, order_items,
    orders, customers, products, sellers CASCADE;

CREATE TABLE customers (
    customer_id TEXT,
    customer_unique_id TEXT
);

CREATE TABLE orders (
    order_id TEXT,
    customer_id TEXT
);

CREATE TABLE products (
    product_id TEXT
);

CREATE TABLE sellers (
    seller_id TEXT
);

CREATE TABLE order_items (
    order_id TEXT,
    order_item_id INTEGER,
    product_id TEXT,
    seller_id TEXT,
    price NUMERIC,
    freight_value NUMERIC
);

CREATE TABLE order_payments (
    order_id TEXT,
    payment_sequential INTEGER,
    payment_value NUMERIC
);

CREATE TABLE order_reviews (
    review_id TEXT,
    order_id TEXT,
    review_score INTEGER
);

INSERT INTO customers VALUES ('customer_1', 'unique_customer_1');
INSERT INTO orders VALUES ('order_1', 'customer_1');
INSERT INTO products VALUES ('product_1');
INSERT INTO sellers VALUES ('seller_1');

INSERT INTO order_items
VALUES ('order_1', 1, 'product_1', 'seller_1', 25.00, 5.00);

INSERT INTO order_payments
VALUES ('order_1', 1, 30.00);

INSERT INTO order_reviews
VALUES ('review_1', 'order_1', 5);