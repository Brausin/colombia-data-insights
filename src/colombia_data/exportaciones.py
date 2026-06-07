"""
exportaciones.py
================
Funciones para analizar las exportaciones colombianas por producto y sector.

Fuente: DANE — Estadísticas de Comercio Exterior
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "exportaciones_colombia.csv"


def _cargar_datos() -> pd.DataFrame:
    """Carga el dataset de exportaciones desde el CSV procesado."""
    if not _DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset no encontrado en {_DATA_PATH}. "
            "Ejecute el script de actualización de datos."
        )
    return pd.read_csv(_DATA_PATH)


def get_exportaciones(
    anio_inicio: int = 2010,
    anio_fin: int = 2024,
    sector: str | None = None,
) -> pd.DataFrame:
    """
    Retorna las exportaciones colombianas por producto y año.

    Parámetros
    ----------
    anio_inicio : int
        Año de inicio del periodo.
    anio_fin : int
        Año de fin del periodo.
    sector : str, opcional
        Filtra por sector: 'Minería', 'Agricultura', 'Manufactura', 'Agroindustria'.
        Si es None, retorna todos.

    Retorna
    -------
    pd.DataFrame
        Columnas: anio, producto, sector, valor_millones_usd.

    Ejemplo
    -------
    >>> df = get_exportaciones(2018, 2024, sector="Agricultura")
    >>> print(df.groupby("anio")["valor_millones_usd"].sum())
    """
    df = _cargar_datos()
    mask = (df["anio"] >= anio_inicio) & (df["anio"] <= anio_fin)
    df = df[mask]

    if sector is not None:
        df = df[df["sector"] == sector]
        if df.empty:
            sectores = _cargar_datos()["sector"].unique().tolist()
            raise ValueError(f"Sector '{sector}' no encontrado. Opciones: {sectores}")

    return df.reset_index(drop=True)


def top_productos(
    anio: int = 2024,
    n: int = 5,
) -> pd.DataFrame:
    """
    Retorna los N productos de exportación con mayor valor para un año dado.

    Parámetros
    ----------
    anio : int
        Año de referencia.
    n : int
        Número de productos a retornar.

    Retorna
    -------
    pd.DataFrame
        Top N productos ordenados por valor descendente.

    Ejemplo
    -------
    >>> top = top_productos(2024, n=5)
    >>> print(top[["producto", "valor_millones_usd"]])
    """
    df = _cargar_datos()
    df_anio = df[df["anio"] == anio].copy()

    if df_anio.empty:
        anios_disponibles = sorted(df["anio"].unique())
        raise ValueError(f"Año {anio} no disponible. Años: {anios_disponibles}")

    resultado = (
        df_anio.sort_values("valor_millones_usd", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    resultado.index = resultado.index + 1  # ranking desde 1
    return resultado
