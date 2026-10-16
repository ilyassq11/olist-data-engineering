import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

connection_url = URL.create(
    "postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(connection_url)

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

# Tutte le tabelle referenziate o referenzianti da svuotare
# vengono incluse nella stessa istruzione TRUNCATE.
tables_to_refresh = [
    "order_reviews",
    "order_payments",
    "order_items",
    "orders",
    "geolocation",
    "category_translation",
    "products",
    "sellers",
]

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


def get_file_path(table):
    if table == "category_translation":
        return BASE_DIR / "data" / "product_category_name_translation.csv"

    return BASE_DIR / "data" / f"olist_{table}_dataset.csv"


def get_db_columns(conn, table):
    result = conn.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table
            ORDER BY ordinal_position
        """),
        {"table": table},
    )
    return [row[0] for row in result]


def main():
    expected_rows = {}
    file_paths = {}

    try:
        # 1. Controlli preliminari: file, intestazioni e conteggi.
        with engine.connect() as conn:
            for table in tables:
                path = get_file_path(table)
                file_paths[table] = path

                if not path.is_file():
                    raise FileNotFoundError(f"File mancante: {path}")

                csv_columns = pd.read_csv(path, nrows=0).columns.tolist()
                db_columns = get_db_columns(conn, table)

                # geolocation_id viene generato dall'ETL.
                if table == "geolocation":
                    db_columns = [
                        col for col in db_columns
                        if col != "geolocation_id"
                    ]

                if csv_columns != db_columns:
                    raise ValueError(
                        f"Colonne non corrispondenti per {table}.\n"
                        f"CSV: {csv_columns}\n"
                        f"DB:  {db_columns}"
                    )

                # Conta le righe a blocchi, senza caricare tutto
                # il dataset in memoria.
                expected_rows[table] = sum(
                    len(chunk)
                    for chunk in pd.read_csv(path, chunksize=50000)
                )

                print(
                    f"Verificato {table}: "
                    f"{expected_rows[table]} righe attese"
                )

        print("\nControlli preliminari completati.")

        # 2. Refresh atomico: se qualcosa fallisce, rollback.
        with engine.begin() as conn:
            conn.execute(
                text(
                    "TRUNCATE TABLE "
                    + ", ".join(tables_to_refresh)
                    + " RESTART IDENTITY"
                )
            )

            for table in tables:
                print(f"\nCaricamento: {table}")

                df = pd.read_csv(file_paths[table])

                for column in date_columns.get(table, []):
                    df[column] = pd.to_datetime(
                        df[column],
                        errors="coerce",
                    )

                if table == "geolocation":
                    df.insert(
                        0,
                        "geolocation_id",
                        range(1, len(df) + 1),
                    )

                df.to_sql(
                    name=table,
                    con=conn,
                    if_exists="append",
                    index=False,
                    chunksize=5000,
                )

                actual_rows = conn.execute(
                    text(f'SELECT COUNT(*) FROM "{table}"')
                ).scalar_one()

                if actual_rows != expected_rows[table]:
                    raise ValueError(
                        f"Conteggio errato per {table}: "
                        f"attese {expected_rows[table]}, "
                        f"trovate {actual_rows}"
                    )

                print(f"Completato: {actual_rows} righe")

        print("\nETL completato: transazione confermata.")

    except Exception:
        print(
            "\nETL fallito. Se l'errore è avvenuto durante "
            "la transazione, PostgreSQL ha annullato il refresh."
        )
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
