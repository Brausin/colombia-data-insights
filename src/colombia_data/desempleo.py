"""
desempleo.py
============
Funciones para analizar el mercado laboral colombiano.

Fuente: DANE — Gran Encuesta Integrada de Hogares (GEIH)
"""

from __future__ import annotations

import pandas as pd
from .fetcher import DANEClient


# Datos históricos de desempleo por ciudad principal (tasa anual promedio %)
# Fuente: DANE GEIH
_DESEMPLEO_CIUDADES = {
    "Bogotá": {
        2018: 9.0, 2019: 9.8, 2020: 16.0, 2021: 13.2,
        2022: 10.4, 2023: 9.8, 2024: 9.2,
    },
    "Medellín AM": {
        2018: 10.9, 2019: 11.3, 2020: 19.1, 2021: 15.1,
        2022: 11.7, 2023: 10.5, 2024: 10.0,
    },
    "Cali AM": {
        2018: 12.5, 2019: 13.1, 2020: 21.6, 2021: 17.0,
        2022: 13.1, 2023: 12.0, 2024: 11.5,
    },
    "Barranquilla AM": {
        2018: 8.4, 2019: 8.9, 2020: 17.2, 2021: 12.8,
        2022: 9.8, 2023: 9.1, 2024: 8.7,
    },
    "Bucaramanga AM": {
        2018: 9.8, 2019: 10.5, 2020: 17.5, 2021: 13.6,
        2022: 10.1, 2023: 9.4, 2024: 8.9,
    },
}


def get_desempleo(
    anio_inicio: int = 2018,
    anio_fin: int = 2024,
    nivel: str = "nacional",
) -> pd.DataFrame:
    """
    Obtiene la tasa de desempleo trimestral o anual por ciudad.

    Parámetros
    ----------
    anio_inicio : int
        Año de inicio.
    anio_fin : int
        Año de fin.
    nivel : str
        'nacional' para serie nacional trimestral, o nombre de ciudad.

    Retorna
    -------
    pd.DataFrame
        Serie de desempleo para el nivel solicitado.

    Ejemplo
    -------
    >>> df = get_desempleo(2020, 2024, nivel="nacional")
    >>> print(df)
    """
    if nivel == "nacional":
        cliente = DANEClient()
        return cliente.obtener_desempleo(anio_inicio=anio_inicio, anio_fin=anio_fin)

    if nivel not in _DESEMPLEO_CIUDADES:
        ciudades_disponibles = list(_DESEMPLEO_CIUDADES.keys())
        raise ValueError(
            f"Ciudad '{nivel}' no disponible. Opciones: {ciudades_disponibles}"
        )

    datos = _DESEMPLEO_CIUDADES[nivel]
    registros = [
        {"anio": anio, "ciudad": nivel, "tasa_desempleo": tasa}
        for anio, tasa in datos.items()
        if anio_inicio <= anio <= anio_fin
    ]
    return pd.DataFrame(registros).reset_index(drop=True)


def comparar_ciudades(
    anio_inicio: int = 2020,
    anio_fin: int = 2024,
) -> pd.DataFrame:
    """
    Compara la tasa de desempleo entre las principales ciudades colombianas.

    Parámetros
    ----------
    anio_inicio : int
        Año de inicio del periodo.
    anio_fin : int
        Año de fin del periodo.

    Retorna
    -------
    pd.DataFrame
        Tabla pivote: filas = ciudades, columnas = años.

    Ejemplo
    -------
    >>> tabla = comparar_ciudades(2020, 2024)
    >>> print(tabla.to_string())
    """
    registros = []
    for ciudad, datos in _DESEMPLEO_CIUDADES.items():
        for anio, tasa in datos.items():
            if anio_inicio <= anio <= anio_fin:
                registros.append({"ciudad": ciudad, "anio": anio, "tasa": tasa})

    df = pd.DataFrame(registros)
    pivot = df.pivot(index="ciudad", columns="anio", values="tasa")
    pivot.columns.name = None
    return pivot
