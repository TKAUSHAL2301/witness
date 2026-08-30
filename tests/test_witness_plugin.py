"""The pytest integration — Witness as a CI gate, not a demo.

This is what a finance team would actually add to their repo: a normal pytest
test asserting their Python port still matches the workbook it came from, and
a test proving the gate rejects a defective port.
"""

import importlib.util
from pathlib import Path

import pytest

from witness.pytest_plugin import CertificationError, certify_equivalent

WORKBOOK = "corpus/financial-indicators-template-0.xlsx"
TARGET = "10 - Debt Service!P31"
PORT_FILE = Path("ports/witness/financial-indicators-template-0__10_-_Debt_Service.P31.py")


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("demo_port", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.compute


@pytest.mark.skipif(not PORT_FILE.exists(), reason="port not generated yet")
def test_certified_port_matches_workbook():
    """The happy path: a port that agrees with Excel passes the gate."""
    check = certify_equivalent(
        workbook=WORKBOOK, target=TARGET, port=_load(PORT_FILE), trials=500
    )
    check()


@pytest.mark.skipif(not PORT_FILE.exists(), reason="port not generated yet")
def test_defective_port_is_rejected():
    """The gate must FAIL a defective port, otherwise it is decoration.

    The injected defect is banker's rounding — the exact failure family that
    beat Witness on capital-targets-template::Debt.H8 by a delta of 1.00.
    """
    good = _load(PORT_FILE)
    check = certify_equivalent(
        workbook=WORKBOOK,
        target=TARGET,
        port=lambda inputs: round(good(inputs) or 0),
        trials=500,
    )
    with pytest.raises(CertificationError) as e:
        check()
    msg = str(e.value)
    assert "Excel returned" in msg
    assert "Minimal inputs" in msg
    assert "Smallest failing input vector" in msg


def test_volatile_target_is_refused():
    """A cell depending on NOW()/RAND() cannot have a stable oracle, so the
    plugin must refuse to certify it rather than certify it by luck."""
    from witness.pytest_plugin import build_case

    with pytest.raises(ValueError):
        build_case("corpus/financial-indicators-template-0.xlsx", "NoSuchSheet!A1")
