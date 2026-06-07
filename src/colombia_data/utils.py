"""
utils.py
========
Utilidades generales para formatear y analizar datos económicos colombianos.
"""

from __future__ import annotations

import pandas as pd


def formatear_pesos(valor: float, decimales: int = 0) -> str:
    """
    Formatea un valor numérico como moneda colombiana (COP).

    Parámetros
    ----------
    valor : float
        Monto en pesos colombianos.
    decimales : int
        Número de decimales a mostrar (por defecto 0).

    Retorna
    -------
    str
        Valor formateado, p. ej. '$ 1.250.000'.

    Ejemplo
    -------
    >>> formatear_pesos(1250000)
    '$ 1.250.000'
    >>> formatear_pesos(15750.5, decimales=2)
    '$ 15.750,50'
    """
    if decimales == 0:
        entero = round(valor)
        return f"$ {entero:,.0f}".replace(",", ".")
    else:
        fmt = f"{valor:,.{decimales}f}"
        # Separador de miles con punto, decimales con coma (estilo colombiano)
        partes = fmt.split(".")
        parte_entera = partes[0].replace(",", ".")
        return f"$ {parte_entera},{partes[1]}"


def calcular_poder_adquisitivo(
    salario: float,
    canasta_basica: float,
) -> dict:
    """
    Calcula el poder adquisitivo de un salario respecto a la canasta básica.

    Parámetros
    ----------
    salario : float
        Ingreso mensual en COP.
    canasta_basica : float
        Costo mensual de la canasta básica familiar en COP.

    Retorna
    -------
    dict
        Indicadores de poder adquisitivo: ratio, excedente, cobertura_pct.

    Ejemplo
    -------
    >>> resultado = calcular_poder_adquisitivo(1_300_000, 980_000)
    >>> print(resultado["cobertura_pct"])
    132.65
    """
    ratio = salario / canasta_basica if canasta_basica > 0 else 0
    excedente = salario - canasta_basica
    cobertura_pct = round(ratio * 100, 2)

    return {
        "salario": salario,
        "canasta_basica": canasta_basica,
        "ratio": round(ratio, 4),
        "excedente_cop": round(excedente, 0),
        "cobertura_pct": cobertura_pct,
        "cubre_canasta": salario >= canasta_basica,
    }


def smmlv(anio: int = 2024) -> int:
    """
    Retorna el Salario Mínimo Mensual Legal Vigente (SMMLV) para el año dado.

    Parámetros
    ----------
    anio : int
        Año de consulta (2015-2025).

    Retorna
    -------
    int
        SMMLV en pesos colombianos.

    Ejemplo
    -------
    >>> smmlv(2024)
    1300000
    """
    _SMMLV = {
        2015: 644_350,
        2016: 689_455,
        2017: 737_717,
        2018: 781_242,
        2019: 828_116,
        2020: 877_803,
        2021: 908_526,
        2022: 1_000_000,
        2023: 1_160_000,
        2024: 1_300_000,
        2025: 1_423_500,
    }
    if anio not in _SMMLV:
        anios_disponibles = sorted(_SMMLV.keys())
        raise ValueError(
            f"SMMLV para {anio} no disponible. Años registrados: {anios_disponibles}"
        )
    return _SMMLV[anio]


def uvt(anio: int = 2024) -> int:
    """
    Retorna el valor de la Unidad de Valor Tributario (UVT) para el año dado.

    Parámetros
    ----------
    anio : int
        Año de consulta (2019-2025).

    Retorna
    -------
    int
        Valor de la UVT en pesos colombianos.

    Ejemplo
    -------
    >>> uvt(2024)
    47065
    """
    _UVT = {
        2019: 34_270,
        2020: 35_607,
        2021: 36_308,
        2022: 38_004,
        2023: 42_412,
        2024: 47_065,
        2025: 49_799,
    }
    if anio not in _UVT:
        anios_disponibles = sorted(_UVT.keys())
        raise ValueError(
            f"UVT para {anio} no disponible. Años registrados: {anios_disponibles}"
        )
    return _UVT[anio]
