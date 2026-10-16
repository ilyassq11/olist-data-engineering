import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "06_data_quality.py"
REPORT_PATH = PROJECT_ROOT / "data_quality_report.csv"


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

    assert len(report) == 17, (
        f"Attesi 17 controlli, trovati {len(report)}."
    )

    assert (report["esito"] == "PASS").all(), (
        "Almeno un controllo di qualità non è stato superato:\n"
        f"{report[report['esito'] != 'PASS'].to_string(index=False)}"
    )
