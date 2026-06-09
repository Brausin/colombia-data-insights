"""
tests/test_inflacion_anual.py
=============================
Pruebas del dataset de inflación anual del Banco Mundial
(data/processed/inflacion_anual.csv) y del formateo del CSV que produce
scripts/actualizar_ipc_anual.py.

No dependen de la red: validan el archivo ya versionado y el escritor del
CSV con datos de ejemplo.
"""

import csv
import importlib.util
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_CSV = _REPO / "data" / "processed" / "inflacion_anual.csv"


def _cargar_filas():
    with open(_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _importar_script():
    spec = importlib.util.spec_from_file_location(
        "actualizar_ipc_anual", _REPO / "scripts" / "actualizar_ipc_anual.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_csv_existe():
    assert _CSV.exists(), "Falta data/processed/inflacion_anual.csv"


def test_csv_tiene_columnas_esperadas():
    filas = _cargar_filas()
    assert filas, "El CSV no tiene filas"
    assert set(filas[0].keys()) == {"anio", "inflacion_pct", "fuente"}


def test_datos_validos_y_unicos():
    filas = _cargar_filas()
    anios = []
    for fila in filas:
        anio = int(fila["anio"])
        pct = float(fila["inflacion_pct"])
        assert 1990 <= anio <= 2100, f"Año fuera de rango: {anio}"
        assert -20 <= pct <= 100, f"Inflación implausible: {pct}"
        assert fila["fuente"].strip(), "Fuente vacía"
        anios.append(anio)
    assert len(anios) == len(set(anios)), "Hay años duplicados"
    assert len(anios) >= 10, "Se esperan al menos 10 años de historia"
    assert anios == sorted(anios), "Los años deben quedar ordenados"


def test_guardar_csv_formatea_encabezado(tmp_path, monkeypatch):
    mod = _importar_script()
    destino = tmp_path / "inflacion_anual.csv"
    monkeypatch.setattr(mod, "_CSV_PATH", destino)
    mod.guardar_csv([(2022, 10.18), (2023, 11.74)])
    lineas = destino.read_text(encoding="utf-8").splitlines()
    assert lineas[0] == "anio,inflacion_pct,fuente"
    assert lineas[1].startswith("2022,10.18,")
    assert lineas[2].startswith("2023,11.74,")
