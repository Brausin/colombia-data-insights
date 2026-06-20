#!/usr/bin/env python3
"""
actualizar_pib_percapita.py — Actualiza el PIB per cápita de Colombia.

Descarga el PIB per cápita en USD corrientes (indicador ``NY.GDP.PCAP.CD``)
desde la API abierta del Banco Mundial y lo guarda en
``data/processed/pib_percapita.csv``.

El indicador mide el Producto Interno Bruto dividido por la población
a mitad de año, expresado en dólares corrientes (no ajustados por inflación).
Es útil para comparaciones internacionales de nivel de vida.

Uso:
    python scripts/actualizar_pib_percapita.py
"""

import csv
import sys
from pathlib import Path

import requests

_INDICADOR = "NY.GDP.PCAP.CD"
_API_URL = (
    "https://api.worldbank.org/v2/country/CO/indicator/"
    f"{_INDICADOR}?format=json&mrv={{mrv}}"
)
_FUENTE = "Banco Mundial - NY.GDP.PCAP.CD (PIB per cápita, USD corrientes)"

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CSV_PATH = _REPO_ROOT / "data" / "processed" / "pib_percapita.csv"


def obtener_pib_percapita(mrv: int = 15) -> list[tuple[int, float]]:
    """Consulta el Banco Mundial y devuelve ``[(anio, pib_usd), ...]``.

    Parámetros
    ----------
    mrv : int
        ``most recent values``: número de años recientes a solicitar.

    Retorna
    -------
    list[tuple[int, float]]
        Pares (año, PIB per cápita USD) ordenados ascendentemente por año.
        Los años sin dato publicado se omiten.
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
    """Escribe el CSV con columnas ``anio,pib_percapita_usd,fuente``."""
    _CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["anio", "pib_percapita_usd", "fuente"])
        for anio, usd in filas:
            writer.writerow([anio, usd, _FUENTE])
    return _CSV_PATH


def main() -> int:
    try:
        filas = obtener_pib_percapita()
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo consultar el Banco Mundial: {exc}")
        return 1

    if not filas:
        print("La API no devolvió datos de PIB. Sin cambios.")
        return 1

    guardar_csv(filas)
    print(
        f"pib_percapita.csv actualizado: {len(filas)} años "
        f"({filas[0][0]}-{filas[-1][0]}), "
        f"último ${filas[-1][1]:,.0f} USD"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
