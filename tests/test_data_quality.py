import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "06_data_quality.py"
REPORT_PATH = PROJECT_ROOT / "data_quality_report.csv"

EXPECTED_CHECKS = 17
REQUIRED_COLUMNS = {"controllo", "problemi", "esito"}


def test_data_quality_checks_pass():
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

    assert REPORT_PATH.exists(), "Il report CSV non è stato generato."

    report = pd.read_csv(REPORT_PATH)

    assert not report.empty, "Il report di qualità è vuoto."
    assert REQUIRED_COLUMNS.issubset(report.columns), (
        f"Colonne mancanti nel report: "
        f"{REQUIRED_COLUMNS - set(report.columns)}"
    )

    assert len(report) == EXPECTED_CHECKS, (
        f"Attesi {EXPECTED_CHECKS} controlli, trovati {len(report)}."
    )

    assert report["controllo"].notna().all(), (
        "Sono presenti controlli senza nome."
    )
    assert report["controllo"].is_unique, (
        "Sono presenti controlli duplicati nel report."
    )

    assert pd.to_numeric(report["problemi"], errors="coerce").notna().all(), (
        "La colonna 'problemi' contiene valori non numerici."
    )
    assert (report["problemi"] >= 0).all(), (
        "La colonna 'problemi' contiene valori negativi."
    )

    assert (report["esito"] == "PASS").all(), (
        "Almeno un controllo di qualità non è stato superato:\n"
        f"{report[report['esito'] != 'PASS'].to_string(index=False)}"
    )
