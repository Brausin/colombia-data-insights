"""
ipc.py
======
Funciones para analizar el Índice de Precios al Consumidor (IPC) de Colombia.

Fuente: Banco de la República / DANE
"""

from __future__ import annotations

import pandas as pd
from .fetcher import BancoRepublicaClient


def get_ipc(anio_inicio: int = 2018, anio_fin: int = 2024) -> pd.DataFrame:
    """
    Obtiene la serie histórica del IPC (variación anual mensual).

    Parámetros
    ----------
    anio_inicio : int
        Año de inicio de la consulta.
    anio_fin : int
        Año de fin de la consulta.

    Retorna
    -------
    pd.DataFrame
        Columnas: fecha, variacion_anual, anio, mes.

    Ejemplo
    -------
    >>> df = get_ipc(2022, 2024)
    >>> print(df.tail())
    """
    cliente = BancoRepublicaClient()
    return cliente.obtener_ipc(anio_inicio=anio_inicio, anio_fin=anio_fin)


def variacion_ipc(df: pd.DataFrame, periodo: str = "anual") -> pd.DataFrame:
    """
    Calcula la variación del IPC para un periodo dado.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame obtenido con get_ipc().
    periodo : str
        'anual' o 'promedio_anual'.

    Retorna
    -------
    pd.DataFrame
        Variación del IPC por periodo.

    Ejemplo
    -------
    >>> df = get_ipc(2020, 2024)
    >>> var = variacion_ipc(df, "promedio_anual")
    >>> print(var)
    """
    if periodo == "promedio_anual":
        resultado = (
            df.groupby("anio")["variacion_anual"]
            .mean()
            .round(2)
            .reset_index()
            .rename(columns={"variacion_anual": "ipc_promedio_anual"})
        )
        return resultado

    elif periodo == "anual":
        return df[["fecha", "variacion_anual"]].copy()

    raise ValueError(f"Periodo '{periodo}' no reconocido. Use 'anual' o 'promedio_anual'.")


def ajustar_por_inflacion(
    valor: float,
    anio_origen: int,
    anio_destino: int,
    df_ipc: pd.DataFrame | None = None,
) -> float:
    """
    Ajusta un valor monetario por inflación entre dos años.

    Usa la inflación promedio anual acumulada entre ambos años.

    Parámetros
    ----------
    valor : float
        Monto original en COP.
    anio_origen : int
        Año del valor original.
    anio_destino : int
        Año al que se desea ajustar.
    df_ipc : pd.DataFrame, opcional
        DataFrame del IPC; si no se provee, se obtiene automáticamente.

    Retorna
    -------
    float
        Valor ajustado por inflación.

    Ejemplo
    -------
    >>> # ¿Cuánto equivale $1.000.000 de 2020 en pesos de 2024?
    >>> ajustar_por_inflacion(1_000_000, 2020, 2024)
    1357842.5
    """
    if df_ipc is None:
        inicio = min(anio_origen, anio_destino)
        fin = max(anio_origen, anio_destino)
        df_ipc = get_ipc(inicio, fin)

    promedios = (
        df_ipc.groupby("anio")["variacion_anual"]
        .mean()
        .div(100)
        .add(1)
    )

    inicio = min(anio_origen, anio_destino)
    fin = max(anio_origen, anio_destino)

    factor = 1.0
    for anio in range(inicio + 1, fin + 1):
        if anio in promedios.index:
            factor *= promedios[anio]

    if anio_destino < anio_origen:
        factor = 1 / factor

    return round(valor * factor, 2)
