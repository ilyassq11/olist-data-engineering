
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "06_data_quality.py"
REPORT_PATH = PROJECT_ROOT / "data_quality_report.csv"

EXPECTED_CHECKS = 17
REQUIRED_COLUMNS = {"controllo", "problemi", "esito"}
DB_VARIABLES = {"DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"}


def test_data_quality_checks_pass():
    env_file_exists = (PROJECT_ROOT / ".env").exists()
    db_env_available = DB_VARIABLES.issubset(os.environ)

    # Esegue i controlli reali quando è disponibile la configurazione DB.
    if env_file_exists or db_env_available:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )

        assert result.returncode == 0, (
            "I controlli di qualità dei dati sono falliti.\n"
            f"Output:\n{result.stdout}\n"
            f"Errori:\n{result.stderr}"
        )

    # In CI verifica il report versionato, senza richiedere credenziali DB.
    assert REPORT_PATH.exists(), "Il report CSV non è disponibile."

    report = pd.read_csv(REPORT_PATH)

    assert not report.empty, "Il report è vuoto."
    assert REQUIRED_COLUMNS.issubset(report.columns), (
        f"Colonne mancanti: {REQUIRED_COLUMNS - set(report.columns)}"
    )
    assert len(report) == EXPECTED_CHECKS, (
        f"Attesi {EXPECTED_CHECKS} controlli, trovati {len(report)}."
    )
    assert report["controllo"].notna().all()
    assert report["controllo"].is_unique
    assert pd.to_numeric(report["problemi"], errors="coerce").notna().all()
    assert (report["problemi"] >= 0).all()
    assert (report["esito"] == "PASS").all(), (
        "Controlli falliti:\n"
        f"{report[report['esito'] != 'PASS'].to_string(index=False)}"
    )
