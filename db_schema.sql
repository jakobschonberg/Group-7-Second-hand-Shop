
PRAGMA foreign_keys = ON;

CREATE TABLE categories(
             category_id INTEGER PRIMARY KEY,
             name TEXT UNIQUE
);

CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL CHECK (price >= 0.0),
            stock INTEGER NOT NULL CHECK (stock >= 0),
            FOREIGN KEY(category_id) REFERENCES categories(category_id)
);

CREATE TABLE customers(
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone_no TEXT,
            city TEXT
);

CREATE TABLE orders(
    order_id INTEGER PRIMARY_KEY,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW' CHECK (status IN ('NEW','DELIVERED','CANCELLED')),
    order_date TEXT NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items(
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
	FOREIGN KEY(order_id) REFERENCES orders(order_id),
	FOREIGN KEY(product_id) REFERENCES products(product_id)
);

-- Use below drop table commands only if you need to drop and create table again
-- DROP TABLES

-- DROP TABLE order_items;
-- DROP TABLE orders;
-- DROP TABLE customers;
-- DROP TABLE products;
-- DROP TABLE categories;