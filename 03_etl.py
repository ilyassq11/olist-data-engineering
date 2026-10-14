
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Percorso principale del progetto
BASE_DIR = Path(__file__).resolve().parent

# Legge le credenziali dal file .env
load_dotenv(BASE_DIR / ".env")

# Crea la connessione a PostgreSQL
connection_url = URL.create(
    "postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(connection_url)

# Dataset da caricare, nell'ordine corretto
tables = [
    "sellers",
    "products",
    "category_translation",
    "geolocation",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
]

# Colonne che contengono date
date_columns = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}

# Caricamento dei dataset
for table in tables:
    file_path = BASE_DIR / "data" / f"olist_{table}_dataset.csv"

    # Il file della traduzione ha un nome diverso
    if table == "category_translation":
        file_path = BASE_DIR / "data" / "product_category_name_translation.csv"

    print(f"\nCaricamento: {table}")

    df = pd.read_csv(file_path)

    # Converte le date prima dell'inserimento
    for column in date_columns.get(table, []):
        df[column] = pd.to_datetime(df[column], errors="coerce")

    # La tabella geolocation ha una chiave creata dal progetto
    if table == "geolocation":
        df.insert(0, "geolocation_id", range(1, len(df) + 1))

    print(f"Righe lette: {len(df)}")

    df.to_sql(
        name=table,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
    )

    print(f"Completato: {table}")

print("\nETL terminato!")
engine.dispose()