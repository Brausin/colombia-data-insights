#!/usr/bin/env python3
"""
actualizar_ipc_anual.py — Actualiza la inflación anual de Colombia.

Descarga la variación anual del IPC (indicador ``FP.CPI.TOTL.ZG``) desde la
API abierta del Banco Mundial y la guarda en
``data/processed/inflacion_anual.csv``.

A diferencia de ``ipc_colombia.csv`` (serie mensual del DANE), este archivo
resume un único dato por año, conveniente para comparaciones de largo plazo
y para gráficos anuales del dashboard.

Uso:
    python scripts/actualizar_ipc_anual.py
"""

import csv
import sys
from pathlib import Path

import requests

# Indicador del Banco Mundial: inflación, precios al consumidor (% anual).
_INDICADOR = "FP.CPI.TOTL.ZG"
_API_URL = (
    "https://api.worldbank.org/v2/country/CO/indicator/"
    f"{_INDICADOR}?format=json&mrv={{mrv}}"
)
_FUENTE = "Banco Mundial - FP.CPI.TOTL.ZG (variación anual del IPC)"

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CSV_PATH = _REPO_ROOT / "data" / "processed" / "inflacion_anual.csv"


def obtener_inflacion_anual(mrv: int = 15) -> list[tuple[int, float]]:
    """Consulta el Banco Mundial y devuelve ``[(anio, inflacion_pct), ...]``.

    Parámetros
    ----------
    mrv : int
        ``most recent values``: número de años recientes a solicitar.

    Retorna
    -------
    list[tuple[int, float]]
        Pares (año, inflación %) ordenados ascendentemente por año. Los
        años sin dato publicado se omiten.
    """
    resp = requests.get(_API_URL.format(mrv=mrv), timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    registros = payload[1] if len(payload) > 1 and payload[1] else []

    filas: list[tuple[int, float]] = []
    for r in registros:
        valor, anio = r.get("value"), r.get("date")
        if valor is None or anio is None:
            continue
        filas.append((int(anio), round(float(valor), 2)))

    filas.sort(key=lambda par: par[0])
    return filas


def guardar_csv(filas: list[tuple[int, float]]) -> Path:
    """Escribe el CSV con columnas ``anio,inflacion_pct,fuente``."""
    _CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["anio", "inflacion_pct", "fuente"])
        for anio, pct in filas:
            writer.writerow([anio, pct, _FUENTE])
    return _CSV_PATH


def main() -> int:
    try:
        filas = obtener_inflacion_anual()
    except Exception as exc:  # noqa: BLE001 — la red puede fallar en CI
        print(f"No se pudo consultar el Banco Mundial: {exc}")
        return 1

    if not filas:
        print("La API no devolvió datos de inflación. Sin cambios.")
        return 1

    guardar_csv(filas)
    print(
        f"inflacion_anual.csv actualizado: {len(filas)} años "
        f"({filas[0][0]}-{filas[-1][0]}), último {filas[-1][1]:.2f}%"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
