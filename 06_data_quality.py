import sys
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# 1. Configurazione e connessione a PostgreSQL
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


# 2. Ogni query conta quanti problemi sono presenti.
#    Per superare il controllo, il numero deve essere zero.
checks = [
    (
        "Duplicati customer_id",
        """
        SELECT COUNT(*) FROM (
            SELECT customer_id
            FROM customers
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        ) AS duplicates
        """,
    ),
    (
        "Duplicati order_id",
        """
        SELECT COUNT(*) FROM (
            SELECT order_id
            FROM orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) AS duplicates
        """,
    ),
    (
        "Duplicati product_id",
        """
        SELECT COUNT(*) FROM (
            SELECT product_id
            FROM products
            GROUP BY product_id
            HAVING COUNT(*) > 1
        ) AS duplicates
        """,
    ),
    (
        "Duplicati seller_id",
        """
        SELECT COUNT(*) FROM (
            SELECT seller_id
            FROM sellers
            GROUP BY seller_id
            HAVING COUNT(*) > 1
        ) AS duplicates
        """,
    ),
    (
        "Duplicati chiave order_items",
        """
        SELECT COUNT(*) FROM (
            SELECT order_id, order_item_id
            FROM order_items
            GROUP BY order_id, order_item_id
            HAVING COUNT(*) > 1
        ) AS duplicates
        """,
    ),
    (
        "Duplicati chiave order_payments",
        """
        SELECT COUNT(*) FROM (
            SELECT order_id, payment_sequential
            FROM order_payments
            GROUP BY order_id, payment_sequential
            HAVING COUNT(*) > 1
        ) AS duplicates
        """,
    ),
    (
        "Duplicati chiave order_reviews",
        """
        SELECT COUNT(*) FROM (
            SELECT review_id, order_id
            FROM order_reviews
            GROUP BY review_id, order_id
            HAVING COUNT(*) > 1
        ) AS duplicates
        """,
    ),
    (
        "Ordini senza cliente",
        """
        SELECT COUNT(*)
        FROM orders o
        LEFT JOIN customers c
            ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
        """,
    ),
    (
        "Articoli senza prodotto",
        """
        SELECT COUNT(*)
        FROM order_items oi
        LEFT JOIN products p
            ON oi.product_id = p.product_id
        WHERE p.product_id IS NULL
        """,
    ),
    (
        "Articoli senza venditore",
        """
        SELECT COUNT(*)
        FROM order_items oi
        LEFT JOIN sellers s
            ON oi.seller_id = s.seller_id
        WHERE s.seller_id IS NULL
        """,
    ),
    (
        "Pagamenti senza ordine",
        """
        SELECT COUNT(*)
        FROM order_payments p
        LEFT JOIN orders o ON p.order_id = o.order_id
        WHERE o.order_id IS NULL
        """,
    ),
    (
        "Recensioni senza ordine",
        """
        SELECT COUNT(*)
        FROM order_reviews r
        LEFT JOIN orders o ON r.order_id = o.order_id
        WHERE o.order_id IS NULL
        """,
    ),
    (
        "Recensioni fuori dall'intervallo 1-5",
        """
        SELECT COUNT(*)
        FROM order_reviews
        WHERE review_score NOT BETWEEN 1 AND 5
           OR review_score IS NULL
        """,
    ),
    (
        "Prezzi negativi",
        """
        SELECT COUNT(*)
        FROM order_items
        WHERE price < 0 OR price IS NULL
        """,
    ),
    (
        "Spese di spedizione negative",
        """
        SELECT COUNT(*)
        FROM order_items
        WHERE freight_value < 0 OR freight_value IS NULL
        """,
    ),
    (
        "Valori pagamento negativi",
        """
        SELECT COUNT(*)
        FROM order_payments
        WHERE payment_value < 0 OR payment_value IS NULL
        """,
    ),
    (
        "Ordini senza identificativo cliente",
        """
        SELECT COUNT(*)
        FROM orders
        WHERE customer_id IS NULL
        """,
    ),
]


# 3. Esecuzione dei controlli
results = []

try:
    with engine.connect() as connection:
        for check_name, query in checks:
            problem_count = connection.execute(text(query)).scalar_one()

            results.append(
                {
                    "controllo": check_name,
                    "problemi": int(problem_count),
                    "esito": "PASS" if problem_count == 0 else "FAIL",
                }
            )

    # 4. Report finale
    report = pd.DataFrame(results)

    print("\n" + "=" * 65)
    print("REPORT DATA QUALITY - OLIST")
    print("=" * 65)
    print(report.to_string(index=False))

    total_checks = len(report)
    passed = int((report["esito"] == "PASS").sum())
    failed = total_checks - passed

    print("\n" + "-" * 65)
    print(f"Controlli eseguiti: {total_checks}")
    print(f"Superati:           {passed}")
    print(f"Falliti:            {failed}")
    print("-" * 65)

    # Salva il report per documentare il progetto
    report_path = BASE_DIR / "data_quality_report.csv"
    report.to_csv(report_path, index=False)

    print(f"\nReport salvato in: {report_path}")

    if failed:
        print("\nATTENZIONE: alcuni controlli richiedono un'indagine.")
        sys.exit(1)
    else:
        print("\nTUTTI I CONTROLLI SONO STATI SUPERATI!")

finally:
    engine.dispose()