"""Tests para el módulo utils.py."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from colombia_data.utils import formatear_pesos, calcular_poder_adquisitivo, smmlv, uvt


def test_formatear_pesos_entero():
    assert formatear_pesos(1_000_000) == "$ 1.000.000"


def test_formatear_pesos_cero():
    assert formatear_pesos(0) == "$ 0"


def test_formatear_pesos_con_decimales():
    resultado = formatear_pesos(15750.5, decimales=2)
    assert resultado.startswith("$ ")
    assert "750" in resultado


def test_calcular_poder_adquisitivo_cubre():
    r = calcular_poder_adquisitivo(1_300_000, 980_000)
    assert r["cubre_canasta"] is True
    assert r["excedente_cop"] > 0
    assert r["cobertura_pct"] > 100


def test_calcular_poder_adquisitivo_no_cubre():
    r = calcular_poder_adquisitivo(500_000, 980_000)
    assert r["cubre_canasta"] is False
    assert r["excedente_cop"] < 0


def test_smmlv_2024():
    assert smmlv(2024) == 1_300_000


def test_smmlv_2022():
    assert smmlv(2022) == 1_000_000


def test_smmlv_anio_invalido():
    with pytest.raises(ValueError):
        smmlv(2000)


def test_uvt_2024():
    assert uvt(2024) == 47_065


def test_uvt_2025():
    assert uvt(2025) == 49_799


def test_uvt_anio_invalido():
    with pytest.raises(ValueError):
        uvt(2010)
