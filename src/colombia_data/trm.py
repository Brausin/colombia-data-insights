"""
colombia_data.trm
=================
Módulo para consultar y analizar la Tasa Representativa del Mercado (TRM)
COP/USD publicada por el Banco de la República de Colombia.

Ejemplo de uso::

    from colombia_data.trm import cargar_trm, trm_en_periodo, variacion_anual

    df = cargar_trm()
    trm_2022 = trm_en_periodo(df, 2022)
    print(f"TRM promedio 2022: {trm_2022['trm_cop_usd'].mean():.0f} COP/USD")
"""

import os
import pandas as pd
from pathlib import Path

# Ruta al dataset procesado relativa a este módulo
_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
_TRM_FILE = _DATA_DIR / "tasa_cambio_usd_cop.csv"


def cargar_trm(ruta: str = None) -> pd.DataFrame:
    """
    Carga el dataset de TRM mensual COP/USD.

    Parámetros
    ----------
    ruta : str, opcional
        Ruta personalizada al archivo CSV. Si no se especifica, usa el
        dataset incluido en el paquete (2010-2024).

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas: año, mes, periodo, trm_cop_usd,
        variacion_mensual_pct, fuente. El índice es el periodo (YYYY-MM).

    Ejemplo
    -------
    >>> df = cargar_trm()
    >>> df.shape
    (180, 6)
    """
    archivo = ruta or _TRM_FILE
    df = pd.read_csv(archivo)
    df["periodo"] = pd.to_datetime(df["periodo"], format="%Y-%m")
    df = df.set_index("periodo").sort_index()
    return df


def trm_en_periodo(
    df: pd.DataFrame, año: int, mes: int = None
) -> pd.DataFrame:
    """
    Filtra la TRM para un año o mes específico.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame cargado con :func:`cargar_trm`.
    año : int
        Año a filtrar (ej. 2022).
    mes : int, opcional
        Mes a filtrar (1-12). Si se omite, retorna todo el año.

    Retorna
    -------
    pd.DataFrame
        Subconjunto filtrado del DataFrame original.

    Ejemplo
    -------
    >>> df = cargar_trm()
    >>> marzo_2020 = trm_en_periodo(df, 2020, 3)
    """
    mask = df["año"] == año
    if mes is not None:
        mask = mask & (df["mes"] == mes)
    return df[mask]


def variacion_anual(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la variación porcentual anual de la TRM (promedio anual).

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame cargado con :func:`cargar_trm`.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas: año, trm_promedio, variacion_anual_pct.
        La variación es respecto al promedio del año anterior.

    Ejemplo
    -------
    >>> df = cargar_trm()
    >>> var = variacion_anual(df)
    >>> print(var[var["año"] == 2020]["variacion_anual_pct"].values[0])
    """
    anual = df.groupby("año")["trm_cop_usd"].mean().reset_index()
    anual.columns = ["año", "trm_promedio"]
    anual["variacion_anual_pct"] = anual["trm_promedio"].pct_change() * 100
    anual["variacion_anual_pct"] = anual["variacion_anual_pct"].round(2)
    return anual


def devaluacion_acumulada(df: pd.DataFrame, año_inicio: int, año_fin: int) -> float:
    """
    Calcula la devaluación acumulada del peso colombiano en un período.

    La devaluación refleja cuánto más caro se volvió el dólar en pesos
    entre el año de inicio y el año final (usando promedios anuales).

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame cargado con :func:`cargar_trm`.
    año_inicio : int
        Primer año del período.
    año_fin : int
        Último año del período.

    Retorna
    -------
    float
        Porcentaje de devaluación acumulada (positivo = peso se devaluó).

    Ejemplo
    -------
    >>> df = cargar_trm()
    >>> dev = devaluacion_acumulada(df, 2010, 2024)
    >>> print(f"El peso se devaluó {dev:.1f}% entre 2010 y 2024")
    """
    promedios = variacion_anual(df).set_index("año")["trm_promedio"]
    trm_inicio = promedios.loc[año_inicio]
    trm_fin = promedios.loc[año_fin]
    return round((trm_fin / trm_inicio - 1) * 100, 2)


def convertir_usd_a_cop(
    valor_usd: float, df: pd.DataFrame, año: int, mes: int
) -> float:
    """
    Convierte un valor en dólares a pesos colombianos usando la TRM histórica.

    Parámetros
    ----------
    valor_usd : float
        Valor en dólares estadounidenses.
    df : pd.DataFrame
        DataFrame cargado con :func:`cargar_trm`.
    año : int
        Año de la TRM a usar.
    mes : int
        Mes de la TRM a usar (1-12).

    Retorna
    -------
    float
        Equivalente en pesos colombianos.

    Ejemplo
    -------
    >>> df = cargar_trm()
    >>> cop = convertir_usd_a_cop(1000, df, 2023, 6)
    >>> print(f"USD 1.000 en junio 2023 = COP {cop:,.0f}")
    """
    fila = trm_en_periodo(df, año, mes)
    if fila.empty:
        raise ValueError(f"No hay datos de TRM para {año}-{mes:02d}")
    trm = fila["trm_cop_usd"].iloc[0]
    return round(valor_usd * trm, 2)
