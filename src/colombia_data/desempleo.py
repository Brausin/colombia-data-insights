"""
desempleo.py
============
Funciones para analizar el mercado laboral colombiano.

Fuente: DANE - Gran Encuesta Integrada de Hogares (GEIH)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd

_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


def _cargar_desempleo() -> pd.DataFrame:
    """Carga el dataset de desempleo desde el archivo procesado."""
    ruta = _DATA_DIR / "desempleo_colombia_2015_2024.csv"
    if not ruta.exists():
        raise FileNotFoundError(f"Dataset de desempleo no encontrado en {ruta}.")
    return pd.read_csv(ruta)


def get_desempleo(
    anio_inicio: int = 2015,
    anio_fin: int = 2024,
    ciudad: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retorna la serie histórica de desempleo para Colombia o una ciudad.

    Parámetros
    ----------
    anio_inicio : int
        Año de inicio del período. Por defecto 2015.
    anio_fin : int
        Año de fin del período. Por defecto 2024.
    ciudad : str, opcional
        Filtra por ciudad (ej: 'Bogotá', 'Medellín', 'Cali'). None = nacional.

    Retorna
    -------
    pd.DataFrame
        DataFrame con la tasa de desempleo y variables relacionadas.

    Ejemplo
    -------
    >>> from colombia_data.desempleo import get_desempleo
    >>> df = get_desempleo(anio_inicio=2020)
    >>> print(df[["anio", "trimestre", "tasa_desempleo"]].head())
    """
    df = _cargar_desempleo()

    col_anio = next(
        (c for c in df.columns if c.lower() in ("anio", "año", "year")),
        df.columns[0]
    )
    df = df[(df[col_anio] >= anio_inicio) & (df[col_anio] <= anio_fin)]

    if ciudad is not None:
        col_ciudad = next(
            (c for c in df.columns if "ciudad" in c.lower() or "dominio" in c.lower()),
            None
        )
        if col_ciudad:
            df = df[df[col_ciudad].str.lower().str.contains(ciudad.lower())]

    return df.reset_index(drop=True)


def comparar_ciudades(
    ciudades: List[str],
    anio: int,
) -> pd.DataFrame:
    """
    Compara la tasa de desempleo entre varias ciudades para un año dado.

    Parámetros
    ----------
    ciudades : list of str
        Lista de ciudades a comparar (ej: ['Bogotá', 'Medellín', 'Cali']).
    anio : int
        Año para la comparación.

    Retorna
    -------
    pd.DataFrame
        DataFrame con ciudad y tasa de desempleo, ordenado de menor a mayor.

    Ejemplo
    -------
    >>> from colombia_data.desempleo import comparar_ciudades
    >>> comp = comparar_ciudades(['Bogotá', 'Medellín', 'Cali', 'Barranquilla'], 2023)
    >>> print(comp.to_string(index=False))
    """
    df_total = _cargar_desempleo()

    col_anio = next(
        (c for c in df_total.columns if c.lower() in ("anio", "año", "year")),
        df_total.columns[0]
    )
    col_ciudad = next(
        (c for c in df_total.columns if "ciudad" in c.lower() or "dominio" in c.lower()),
        None
    )
    col_tasa = next(
        (c for c in df_total.columns if "desempleo" in c.lower() or "tasa" in c.lower()),
        None
    )

    if col_ciudad is None or col_tasa is None:
        raise ValueError("No se encontraron columnas de ciudad o tasa en el dataset.")

    df_anio = df_total[df_total[col_anio] == anio]
    resultados = []

    for ciudad in ciudades:
        df_ciudad = df_anio[df_anio[col_ciudad].str.lower().str.contains(ciudad.lower())]
        if not df_ciudad.empty:
            tasa_promedio = df_ciudad[col_tasa].mean()
            resultados.append({"ciudad": ciudad, "tasa_desempleo_pct": round(tasa_promedio, 1)})

    if not resultados:
        raise ValueError(f"No se encontraron datos para las ciudades solicitadas en {anio}.")

    return pd.DataFrame(resultados).sort_values("tasa_desempleo_pct").reset_index(drop=True)


def promedio_anual(ciudad: Optional[str] = None) -> pd.DataFrame:
    """
    Calcula el promedio anual de la tasa de desempleo.

    Parámetros
    ----------
    ciudad : str, opcional
        Ciudad específica. Si es None, usa datos nacionales.

    Retorna
    -------
    pd.DataFrame
        Columnas: anio, tasa_desempleo_promedio_pct.
    """
    df = _cargar_desempleo()
    col_anio = next(
        (c for c in df.columns if c.lower() in ("anio", "año", "year")),
        df.columns[0]
    )
    col_tasa = next(
        (c for c in df.columns if "desempleo" in c.lower() or "tasa" in c.lower()),
        None
    )
    if col_tasa is None:
        raise ValueError("No se encontró columna de tasa de desempleo.")

    if ciudad:
        col_ciudad = next(
            (c for c in df.columns if "ciudad" in c.lower() or "dominio" in c.lower()),
            None
        )
        if col_ciudad:
            df = df[df[col_ciudad].str.lower().str.contains(ciudad.lower())]

    return (
        df.groupby(col_anio)[col_tasa]
        .mean()
        .round(1)
        .reset_index()
        .rename(columns={col_anio: "anio", col_tasa: "tasa_desempleo_promedio_pct"})
    )
