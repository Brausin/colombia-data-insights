#!/usr/bin/env python3
"""
actualizar_trm.py — Actualiza el CSV de TRM con el valor del día.

Consulta la API oficial de datos.gov.co y agrega el registro
si no existe ya para la fecha actual.
"""

import csv
import os
import requests
from datetime import date
from pathlib import Path

_API_URL = (
    "https://www.datos.gov.co/resource/32sa-8pi3.json"
    "?$limit=1&$order=vigenciadesde%20DESC"
)
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CSV_PATH = _REPO_ROOT / "data" / "processed" / "tasa_cambio_usd_cop.csv"

HOY = date.today()
MES_ACTUAL = HOY.strftime("%Y-%m")


def obtener_trm_api() -> float | None:
    try:
        resp = requests.get(_API_URL, timeout=15)
        resp.raise_for_status()
        datos = resp.json()
        if datos and "valor" in datos[0]:
            return float(datos[0]["valor"])
    except Exception as e:
        print(f"API no disponible: {e}")
    return None


def csv_tiene_mes(mes: str) -> bool:
    if not _CSV_PATH.exists():
        return False
    with open(_CSV_PATH, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return any(fila.get("periodo", "").startswith(mes) for fila in filas)


def agregar_registro(trm: float) -> None:
    existe = _CSV_PATH.exists()
    with open(_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["año", "mes", "periodo", "trm_cop_usd", "variacion_mensual_pct", "fuente"])
        writer.writerow([
            HOY.year,
            HOY.month,
            MES_ACTUAL,
            round(trm, 2),
            "",
            "Banco de la República de Colombia - TRM",
        ])
    print(f"TRM {MES_ACTUAL}: {trm:,.2f} COP/USD agregada al CSV")


if __name__ == "__main__":
    if csv_tiene_mes(MES_ACTUAL):
        print(f"Ya existe registro para {MES_ACTUAL}. Sin cambios.")
    else:
        trm = obtener_trm_api()
        if trm:
            agregar_registro(trm)
        else:
            print("No se pudo obtener TRM. Sin cambios.")
