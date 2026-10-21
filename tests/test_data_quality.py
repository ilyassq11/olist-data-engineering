
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "06_data_quality.py"
REPORT_PATH = PROJECT_ROOT / "data_quality_report.csv"

EXPECTED_CHECKS = 17
REQUIRED_COLUMNS = {"controllo", "problemi", "esito"}


def run_quality_script():
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_data_quality_checks_pass():
    load_dotenv(PROJECT_ROOT / ".env")

    if not os.environ.get("DB_USER") or not os.environ.get("DB_NAME"):
        pytest.skip("Database non configurato.")

    result = run_quality_script()
    assert result.returncode == 0, (
        f"Controlli falliti.\nOutput:\n{result.stdout}\nErrori:\n{result.stderr}"
    )

    assert REPORT_PATH.exists(), "Report CSV non trovato."
    report = pd.read_csv(REPORT_PATH)

    assert not report.empty
    assert REQUIRED_COLUMNS.issubset(report.columns)
    assert len(report) == EXPECTED_CHECKS
    assert report["controllo"].notna().all()
    assert report["controllo"].is_unique
    assert pd.to_numeric(report["problemi"], errors="coerce").notna().all()
    assert (report["problemi"] >= 0).all()
    assert (report["esito"] == "PASS").all()


def test_detects_duplicate_customer_in_ci_database():
    # Non inserisce dati di prova nel database personale.
    if os.environ.get("DB_NAME") != "olist_test":
        pytest.skip("Test con dati anomali riservato al database CI.")

    connection_url = URL.create(
        "postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )
    engine = create_engine(connection_url)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO customers (customer_id, customer_unique_id) "
                    "VALUES ('customer_1', 'duplicate_test')"
                )
            )

        result = run_quality_script()

        assert result.returncode == 1, (
            "Il controllo avrebbe dovuto rilevare il duplicato.\n"
            f"Output:\n{result.stdout}\nErrori:\n{result.stderr}"
        )

        report = pd.read_csv(REPORT_PATH)
        duplicate_check = report[
            report["controllo"] == "Duplicati customer_id"
        ]

        assert len(duplicate_check) == 1
        assert duplicate_check.iloc[0]["problemi"] > 0
        assert duplicate_check.iloc[0]["esito"] == "FAIL"

    
    finally:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM customers "
                    "WHERE customer_id = 'customer_1' "
                    "AND customer_unique_id = 'duplicate_test'"
                )
            )
        engine.dispose()

        # Rigenera il report dopo aver ripristinato i dati puliti.
        cleanup_result = run_quality_script()
        assert cleanup_result.returncode == 0, (
            "Il report non è stato ripristinato dopo il test negativo.\n"
            f"Output:\n{cleanup_result.stdout}\n"
            f"Errori:\n{cleanup_result.stderr}"
        )

