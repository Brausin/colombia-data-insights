"""
exportaciones.py
================
Funciones para analizar las exportaciones colombianas por producto y destino.

Fuente: DANE - Estadísticas de Comercio Exterior / DIAN
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd

_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


def _cargar_exportaciones() -> pd.DataFrame:
    """Carga el dataset de exportaciones desde el archivo procesado."""
    ruta = _DATA_DIR / "exportaciones_colombia.csv"
    if not ruta.exists():
        raise FileNotFoundError(f"Dataset de exportaciones no encontrado en {ruta}.")
    return pd.read_csv(ruta)


def get_exportaciones(
    anio_inicio: int = 2010,
    anio_fin: int = 2024,
    producto: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retorna las exportaciones colombianas filtradas por período y/o producto.

    Parámetros
    ----------
    anio_inicio : int
        Año de inicio del período. Por defecto 2010.
    anio_fin : int
        Año de fin del período. Por defecto 2024.
    producto : str, opcional
        Filtra por producto específico (ej: 'Cafe', 'Carbon', 'Flores').

    Retorna
    -------
    pd.DataFrame
        Columnas: anio, producto, valor_millones_usd, participacion_pct, destino_principal.

    Ejemplo
    -------
    >>> from colombia_data.exportaciones import get_exportaciones
    >>> cafe = get_exportaciones(anio_inicio=2018, producto='Cafe')
    >>> print(cafe)
    """
    df = _cargar_exportaciones()
    df = df[(df["anio"] >= anio_inicio) & (df["anio"] <= anio_fin)]

    if producto is not None:
        df = df[df["producto"].str.lower().str.contains(producto.lower())]

    return df.reset_index(drop=True)


def top_productos(
    anio: Optional[int] = None,
    n: int = 5,
) -> pd.DataFrame:
    """
    Retorna los N productos de exportación más importantes por valor.

    Parámetros
    ----------
    anio : int, opcional
        Año específico para el ranking. Si es None, promedia todos los años disponibles.
    n : int
        Número de productos a retornar. Por defecto 5.

    Retorna
    -------
    pd.DataFrame
        DataFrame ordenado de mayor a menor con columnas: producto, valor_millones_usd,
        participacion_pct.

    Ejemplo
    -------
    >>> from colombia_data.exportaciones import top_productos
    >>> ranking = top_productos(anio=2024, n=5)
    >>> print(ranking.to_string(index=False))
    """
    df = _cargar_exportaciones()

    if anio is not None:
        df = df[df["anio"] == anio]
        resultado = (
            df.groupby("producto")["valor_millones_usd"]
            .sum()
            .reset_index()
            .sort_values("valor_millones_usd", ascending=False)
            .head(n)
        )
    else:
        resultado = (
            df.groupby("producto")["valor_millones_usd"]
            .mean()
            .reset_index()
            .rename(columns={"valor_millones_usd": "promedio_millones_usd"})
            .sort_values("promedio_millones_usd", ascending=False)
            .head(n)
        )

    return resultado.reset_index(drop=True)


def evolucion_producto(producto: str) -> pd.DataFrame:
    """
    Retorna la serie histórica anual de un producto de exportación.

    Parámetros
    ----------
    producto : str
        Nombre del producto (ej: 'Cafe', 'Petroleo y derivados').

    Retorna
    -------
    pd.DataFrame
        Serie con columnas: anio, valor_millones_usd, participacion_pct.

    Ejemplo
    -------
    >>> from colombia_data.exportaciones import evolucion_producto
    >>> hist = evolucion_producto('Cafe')
    >>> print(hist)
    """
    return get_exportaciones(producto=producto)[["anio", "valor_millones_usd", "participacion_pct"]]


def total_por_anio(anio_inicio: int = 2010, anio_fin: int = 2024) -> pd.DataFrame:
    """
    Calcula el valor total de exportaciones por año.

    Parámetros
    ----------
    anio_inicio : int
        Año inicial del período.
    anio_fin : int
        Año final del período.

    Retorna
    -------
    pd.DataFrame
        Columnas: anio, total_millones_usd, variacion_anual_pct.
    """
    df = get_exportaciones(anio_inicio=anio_inicio, anio_fin=anio_fin)
    totales = df.groupby("anio")["valor_millones_usd"].sum().reset_index()
    totales.columns = ["anio", "total_millones_usd"]
    totales["variacion_anual_pct"] = totales["total_millones_usd"].pct_change() * 100
    totales["variacion_anual_pct"] = totales["variacion_anual_pct"].round(1)
    return totales
