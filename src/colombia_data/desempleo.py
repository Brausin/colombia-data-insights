"""
desempleo.py
============
Funciones para analizar el mercado laboral colombiano.

Fuente: DANE - Gran Encuesta Integrada de Hogares (GEIH)

El dataset está en formato ancho: cada ciudad es una columna.
Columnas: año, trimestre, periodo, tasa_nacional, bogota, medellin,
          cali, barranquilla, bucaramanga, manizales, ibague, pereira,
          cucuta, cartagena
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd

_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

# Ciudades disponibles en el dataset (columnas del CSV)
CIUDADES_DISPONIBLES = [
    "bogota", "medellin", "cali", "barranquilla", "bucaramanga",
    "manizales", "ibague", "pereira", "cucuta", "cartagena",
]


def _cargar_desempleo() -> pd.DataFrame:
    """Carga el dataset de desempleo desde el archivo procesado."""
    ruta = _DATA_DIR / "desempleo_colombia_2015_2024.csv"
    if not ruta.exists():
        raise FileNotFoundError(f"Dataset de desempleo no encontrado en {ruta}.")
    return pd.read_csv(ruta)


def _normalizar_ciudad(nombre: str) -> Optional[str]:
    """
    Normaliza el nombre de una ciudad para coincidir con las columnas del CSV.

    Parámetros
    ----------
    nombre : str
        Nombre de la ciudad (ej: 'Bogotá', 'MEDELLÍN', 'bogota').

    Retorna
    -------
    str o None
        Nombre de columna correspondiente, o None si no se encuentra.
    """
    nombre_limpio = (
        nombre.lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ü", "u")
        .strip()
    )
    # Búsqueda exacta
    if nombre_limpio in CIUDADES_DISPONIBLES:
        return nombre_limpio
    # Búsqueda parcial
    for ciudad in CIUDADES_DISPONIBLES:
        if ciudad in nombre_limpio or nombre_limpio in ciudad:
            return ciudad
    return None


def get_desempleo(
    anio_inicio: int = 2015,
    anio_fin: int = 2024,
    ciudad: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retorna la serie histórica de desempleo para Colombia o una ciudad.

    El dataset contiene datos trimestrales desde 2015 hasta 2024.

    Parámetros
    ----------
    anio_inicio : int
        Año de inicio del período. Por defecto 2015.
    anio_fin : int
        Año de fin del período. Por defecto 2024.
    ciudad : str, opcional
        Filtra por ciudad (ej: 'Bogotá', 'Medellín', 'Cali').
        Si es None, retorna datos nacionales. Case-insensitive,
        acepta nombres con o sin tilde.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas: año, trimestre, periodo, tasa_desempleo.
        La columna tasa_desempleo es nacional o de la ciudad indicada.

    Ejemplo
    -------
    >>> from colombia_data.desempleo import get_desempleo
    >>> df = get_desempleo(anio_inicio=2020)
    >>> print(df[["año", "trimestre", "tasa_desempleo"]].head())
    """
    df = _cargar_desempleo()
    df = df[(df["año"] >= anio_inicio) & (df["año"] <= anio_fin)].copy()

    if ciudad is not None:
        col = _normalizar_ciudad(ciudad)
        if col is None:
            raise ValueError(
                f"Ciudad '{ciudad}' no encontrada. Ciudades disponibles: "
                + ", ".join(CIUDADES_DISPONIBLES)
            )
        df = df[["año", "trimestre", "periodo", col]].rename(
            columns={col: "tasa_desempleo"}
        )
    else:
        df = df[["año", "trimestre", "periodo", "tasa_nacional"]].rename(
            columns={"tasa_nacional": "tasa_desempleo"}
        )

    return df.reset_index(drop=True)


def comparar_ciudades(
    ciudades: List[str],
    anio: int,
) -> pd.DataFrame:
    """
    Compara la tasa de desempleo entre varias ciudades para un año dado.

    Calcula el promedio de los cuatro trimestres disponibles.

    Parámetros
    ----------
    ciudades : list of str
        Lista de ciudades a comparar (ej: ['Bogotá', 'Medellín', 'Cali']).
        Acepta nombres con o sin tilde, case-insensitive.
    anio : int
        Año para la comparación (2015-2024).

    Retorna
    -------
    pd.DataFrame
        Columnas: ciudad, tasa_desempleo_pct.
        Ordenado de menor a mayor desempleo.

    Ejemplo
    -------
    >>> from colombia_data.desempleo import comparar_ciudades
    >>> comp = comparar_ciudades(['Bogotá', 'Medellín', 'Cali', 'Barranquilla'], 2023)
    >>> print(comp.to_string(index=False))
    """
    df = _cargar_desempleo()
    df_anio = df[df["año"] == anio]

    if df_anio.empty:
        raise ValueError(f"No hay datos para el año {anio}. Rango disponible: 2015-2024.")

    resultados = []
    for ciudad in ciudades:
        col = _normalizar_ciudad(ciudad)
        if col is None:
            raise ValueError(
                f"Ciudad '{ciudad}' no encontrada. Ciudades disponibles: "
                + ", ".join(CIUDADES_DISPONIBLES)
            )
        tasa_prom = df_anio[col].mean()
        resultados.append({"ciudad": ciudad, "tasa_desempleo_pct": round(tasa_prom, 1)})

    return (
        pd.DataFrame(resultados)
        .sort_values("tasa_desempleo_pct")
        .reset_index(drop=True)
    )


def promedio_anual(ciudad: Optional[str] = None) -> pd.DataFrame:
    """
    Calcula el promedio anual de la tasa de desempleo.

    Parámetros
    ----------
    ciudad : str, opcional
        Ciudad específica (ej: 'Bogotá'). Si es None, usa tasa nacional.
        Acepta nombres con o sin tilde, case-insensitive.

    Retorna
    -------
    pd.DataFrame
        Columnas: anio, tasa_desempleo_promedio_pct.

    Ejemplo
    -------
    >>> from colombia_data.desempleo import promedio_anual
    >>> pa = promedio_anual()
    >>> print(pa)
    """
    df = _cargar_desempleo()

    if ciudad is not None:
        col = _normalizar_ciudad(ciudad)
        if col is None:
            raise ValueError(
                f"Ciudad '{ciudad}' no encontrada. Ciudades disponibles: "
                + ", ".join(CIUDADES_DISPONIBLES)
            )
        col_tasa = col
    else:
        col_tasa = "tasa_nacional"

    return (
        df.groupby("año")[col_tasa]
        .mean()
        .round(1)
        .reset_index()
        .rename(columns={"año": "anio", col_tasa: "tasa_desempleo_promedio_pct"})
    )
