"""
ipc.py
======
Funciones para analizar el Índice de Precios al Consumidor (IPC) de Colombia.

Fuente: DANE - Encuesta Nacional de Presupuestos de los Hogares
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd

_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


def _cargar_ipc() -> pd.DataFrame:
    """Carga el dataset de IPC desde el archivo procesado."""
    ruta = _DATA_DIR / "ipc_colombia.csv"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de IPC en {ruta}. "
            "Asegúrese de haber descargado los datos."
        )
    df = pd.read_csv(ruta, parse_dates=["fecha"] if "fecha" in pd.read_csv(ruta, nrows=0).columns else [])
    return df


def get_ipc(
    anio_inicio: int = 2015,
    anio_fin: int = 2024,
    ciudad: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retorna la serie histórica del IPC para Colombia o una ciudad específica.

    Parámetros
    ----------
    anio_inicio : int
        Año de inicio del período (inclusive). Por defecto 2015.
    anio_fin : int
        Año de fin del período (inclusive). Por defecto 2024.
    ciudad : str, opcional
        Filtra por ciudad (ej: 'Bogotá', 'Medellín'). Si es None, retorna nacional.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas: anio, mes (si aplica), ipc, variacion_mensual_pct,
        variacion_anual_pct.

    Ejemplo
    -------
    >>> from colombia_data.ipc import get_ipc
    >>> df = get_ipc(anio_inicio=2020, anio_fin=2024)
    >>> print(df.tail())
    """
    df = _cargar_ipc()

    col_anio = next((c for c in df.columns if "anio" in c.lower() or "año" in c.lower() or "year" in c.lower()), None)
    if col_anio is None and "fecha" in df.columns:
        df["anio"] = pd.to_datetime(df["fecha"]).dt.year
        col_anio = "anio"

    if col_anio:
        df = df[(df[col_anio] >= anio_inicio) & (df[col_anio] <= anio_fin)]

    if ciudad is not None:
        col_ciudad = next((c for c in df.columns if "ciudad" in c.lower()), None)
        if col_ciudad:
            df = df[df[col_ciudad].str.lower() == ciudad.lower()]

    return df.reset_index(drop=True)


def variacion_ipc(
    anio_inicio: int,
    anio_fin: int,
    ciudad: Optional[str] = None,
) -> float:
    """
    Calcula la variación acumulada del IPC entre dos años.

    Parámetros
    ----------
    anio_inicio : int
        Año base para el cálculo.
    anio_fin : int
        Año final para el cálculo.
    ciudad : str, opcional
        Ciudad específica. Si es None, usa el IPC nacional.

    Retorna
    -------
    float
        Variación porcentual acumulada del IPC en el período.

    Ejemplo
    -------
    >>> from colombia_data.ipc import variacion_ipc
    >>> var = variacion_ipc(2020, 2024)
    >>> print(f"Inflación acumulada 2020-2024: {var:.1f}%")
    """
    df = get_ipc(anio_inicio=anio_inicio, anio_fin=anio_fin, ciudad=ciudad)

    col_variacion = next(
        (c for c in df.columns if "variacion_anual" in c.lower() or "variacion" in c.lower()),
        None
    )
    if col_variacion is None:
        raise ValueError("No se encontró columna de variación en el dataset de IPC.")

    col_anio = next((c for c in df.columns if "anio" in c.lower()), "anio")
    df_agrupado = df.groupby(col_anio)[col_variacion].mean()

    # Cálculo de variación acumulada compuesta
    variacion_acumulada = 1.0
    for tasa in df_agrupado.values:
        variacion_acumulada *= (1 + tasa / 100)

    return round((variacion_acumulada - 1) * 100, 2)


def ajustar_por_inflacion(
    valor: float,
    anio_origen: int,
    anio_destino: int,
    ciudad: Optional[str] = None,
) -> float:
    """
    Ajusta un valor monetario por inflación entre dos períodos.

    Útil para comparar valores reales a pesos constantes de un año base.

    Parámetros
    ----------
    valor : float
        Monto en pesos colombianos a ajustar.
    anio_origen : int
        Año en que se expresó el valor original.
    anio_destino : int
        Año al que se quiere llevar el valor.
    ciudad : str, opcional
        Usa el IPC de una ciudad específica.

    Retorna
    -------
    float
        Valor ajustado en pesos del año destino.

    Ejemplo
    -------
    >>> from colombia_data.ipc import ajustar_por_inflacion
    >>> # ¿Cuánto valdrían hoy $1.000.000 de 2015?
    >>> valor_hoy = ajustar_por_inflacion(1_000_000, 2015, 2024)
    >>> print(f"${valor_hoy:,.0f} pesos de 2024")
    """
    if anio_origen == anio_destino:
        return valor

    inicio, fin = (anio_origen, anio_destino) if anio_origen < anio_destino else (anio_destino, anio_origen)
    variacion = variacion_ipc(inicio, fin, ciudad=ciudad)
    factor = 1 + variacion / 100

    if anio_origen < anio_destino:
        return round(valor * factor, 2)
    else:
        return round(valor / factor, 2)
