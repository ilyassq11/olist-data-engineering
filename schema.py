import pandas as pd

order_reviews = pd.read_csv(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\data\olist_order_reviews_dataset.csv"
)

schema = pd.DataFrame({
    "table_name": [
        "orders",
        "customers",
        "order_items",
        "products",
        "sellers",
        "order_payments",
        "order_reviews",
        "category_translation",
        "geolocation"
    ],
    "primary_key": [
        "order_id",
        "customer_id",
        "order_id + order_item_id",
        "product_id",
        "seller_id",
        "order_id + payment_sequential",
        "da definire",
        "product_category_name",
        "da definire"
    ]
})

print(schema)

schema.loc[
    schema["table_name"] == "order_reviews",
    "primary_key"
] = "review_id + order_id"

print(schema)

schema.loc[
    schema["table_name"] == "geolocation",
    "primary_key"
] = "geolocation_id"

print(schema)

print(
    "Duplicati review_id + order_id:",
    order_reviews.duplicated(
        subset=["review_id", "order_id"]
    ).sum()
)

relationships = pd.DataFrame([
    ["orders", "customer_id", "customers", "customer_id"],
    ["order_items", "order_id", "orders", "order_id"],
    ["order_items", "product_id", "products", "product_id"],
    ["order_items", "seller_id", "sellers", "seller_id"],
    ["order_payments", "order_id", "orders", "order_id"],
    ["order_reviews", "order_id", "orders", "order_id"],
    ["products", "product_category_name", "category_translation", "product_category_name"]
], columns=["table", "foreign_key", "references_table", "references_column"])

print("\nRELAZIONI:")
print(relationships)


columns = {
    "orders": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],

    "customers": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ],

    "order_items": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value"
    ],

    "products": [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ],

    "sellers": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state"
    ],

    "order_payments": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value"
    ],

    "order_reviews": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp"
    ],

    "category_translation": [
        "product_category_name",
        "product_category_name_english"
    ],

    "geolocation": [
        "geolocation_id",
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state"
    ]
}

print("\nCOLONNE DELLE TABELLE:")

for table, cols in columns.items():
    print(f"\n{table}:")
    for col in cols:
        print(f"  - {col}")

sql_types = {
    "orders": {
        "order_id": "VARCHAR(32)",
        "customer_id": "VARCHAR(32)",
        "order_status": "VARCHAR(20)",
        "order_purchase_timestamp": "TIMESTAMP",
        "order_approved_at": "TIMESTAMP",
        "order_delivered_carrier_date": "TIMESTAMP",
        "order_delivered_customer_date": "TIMESTAMP",
        "order_estimated_delivery_date": "TIMESTAMP"
    },

    "customers": {
        "customer_id": "VARCHAR(32)",
        "customer_unique_id": "VARCHAR(32)",
        "customer_zip_code_prefix": "INTEGER",
        "customer_city": "VARCHAR(100)",
        "customer_state": "CHAR(2)"
    },

    "order_items": {
        "order_id": "VARCHAR(32)",
        "order_item_id": "INTEGER",
        "product_id": "VARCHAR(32)",
        "seller_id": "VARCHAR(32)",
        "shipping_limit_date": "TIMESTAMP",
        "price": "DECIMAL(10,2)",
        "freight_value": "DECIMAL(10,2)"
    },

    "products": {
        "product_id": "VARCHAR(32)",
        "product_category_name": "VARCHAR(100)",
        "product_name_lenght": "INTEGER",
        "product_description_lenght": "INTEGER",
        "product_photos_qty": "INTEGER",
        "product_weight_g": "INTEGER",
        "product_length_cm": "INTEGER",
        "product_height_cm": "INTEGER",
        "product_width_cm": "INTEGER"
    },

    "sellers": {
        "seller_id": "VARCHAR(32)",
        "seller_zip_code_prefix": "INTEGER",
        "seller_city": "VARCHAR(100)",
        "seller_state": "CHAR(2)"
    },

    "order_payments": {
        "order_id": "VARCHAR(32)",
        "payment_sequential": "INTEGER",
        "payment_type": "VARCHAR(20)",
        "payment_installments": "INTEGER",
        "payment_value": "DECIMAL(10,2)"
    },

    "order_reviews": {
        "review_id": "VARCHAR(32)",
        "order_id": "VARCHAR(32)",
        "review_score": "INTEGER",
        "review_comment_title": "TEXT",
        "review_comment_message": "TEXT",
        "review_creation_date": "TIMESTAMP",
        "review_answer_timestamp": "TIMESTAMP"
    },

    "category_translation": {
        "product_category_name": "VARCHAR(100)",
        "product_category_name_english": "VARCHAR(100)"
    },

    "geolocation": {
        "geolocation_id": "BIGINT",
        "geolocation_zip_code_prefix": "INTEGER",
        "geolocation_lat": "DECIMAL(9,6)",
        "geolocation_lng": "DECIMAL(9,6)",
        "geolocation_city": "VARCHAR(100)",
        "geolocation_state": "CHAR(2)"
    }
}


print("\nTIPI SQL:")

for table, cols in sql_types.items():
    print(f"\n{table}:")
    for col, sql_type in cols.items():
        print(f"  - {col}: {sql_type}")


primary_keys = {
    "orders": ["order_id"],
    "customers": ["customer_id"],
    "order_items": ["order_id", "order_item_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "order_payments": ["order_id", "payment_sequential"],
    "order_reviews": ["review_id", "order_id"],
    "category_translation": ["product_category_name"],
    "geolocation": ["geolocation_id"]
}


not_null = {
    "orders": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_estimated_delivery_date"
    ],

    "customers": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ],

    "order_items": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value"
    ],

    "products": [
        "product_id"
    ],

    "sellers": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state"
    ],

    "order_payments": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value"
    ],

    "order_reviews": [
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "review_answer_timestamp"
    ],

    "category_translation": [
        "product_category_name"
    ],

    "geolocation": [
        "geolocation_id",
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state"
    ]
}



print("\nPRIMARY KEYS:")

for table, keys in primary_keys.items():
    print(f"{table}: {', '.join(keys)}")

print("\nNOT NULL:")

for table, cols in not_null.items():
    print(f"{table}: {', '.join(cols)}")


foreign_keys = [
    {
        "table": "orders",
        "column": "customer_id",
        "references_table": "customers",
        "references_column": "customer_id"
    },
    {
        "table": "order_items",
        "column": "order_id",
        "references_table": "orders",
        "references_column": "order_id"
    },
    {
        "table": "order_items",
        "column": "product_id",
        "references_table": "products",
        "references_column": "product_id"
    },
    {
        "table": "order_items",
        "column": "seller_id",
        "references_table": "sellers",
        "references_column": "seller_id"
    },
    {
        "table": "order_payments",
        "column": "order_id",
        "references_table": "orders",
        "references_column": "order_id"
    },
    {
        "table": "order_reviews",
        "column": "order_id",
        "references_table": "orders",
        "references_column": "order_id"
    }
]

check_constraints = [
    ("order_items", "price >= 0"),
    ("order_items", "freight_value >= 0"),
    ("products", "product_weight_g >= 0"),
    ("products", "product_photos_qty >= 0"),
    ("order_payments", "payment_value >= 0"),
    ("order_payments", "payment_installments >= 0"),
    ("order_reviews", "review_score BETWEEN 1 AND 5")
]


print("\nFOREIGN KEYS:")

for fk in foreign_keys:
    print(
        f"{fk['table']}.{fk['column']} → "
        f"{fk['references_table']}.{fk['references_column']}"
    )

print("\nCHECK CONSTRAINTS:")

for table, condition in check_constraints:
    print(f"{table}: {condition}")



def genera_create_table(table):
    colonne_sql = []

    for colonna, tipo in sql_types[table].items():
        definizione = f"    {colonna} {tipo}"

        if colonna in not_null.get(table, []):
            definizione += " NOT NULL"

        colonne_sql.append(definizione)

    # PRIMARY KEY
    pk = primary_keys[table]
    colonne_sql.append(
        f"    PRIMARY KEY ({', '.join(pk)})"
    )

    # FOREIGN KEY
    for fk in foreign_keys:
        if fk["table"] == table:
            colonne_sql.append(
                f"    FOREIGN KEY ({fk['column']}) "
                f"REFERENCES {fk['references_table']} "
                f"({fk['references_column']})"
            )

    # CHECK
    for check_table, condition in check_constraints:
        if check_table == table:
            colonne_sql.append(
                f"    CHECK ({condition})"
            )

    return (
        f"CREATE TABLE {table} (\n"
        + ",\n".join(colonne_sql)
        + "\n);"
    )

table_order = [
    "customers",
    "sellers",
    "products",
    "category_translation",
    "geolocation",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews"
]

sql_statements = []

for table in table_order:
    sql_statements.append(
        genera_create_table(table)
    )

sql_script = "\n\n".join(sql_statements)

with open(
    r"C:\Users\ilyas\Desktop\olist-data-engineering\01_create_schema.sql",
    "w",
    encoding="utf-8"
) as file:
    file.write(sql_script)

print("\nFile SQL creato:")
print("01_create_schema.sql")


