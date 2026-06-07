"""
utils.py
========
Funciones utilitarias para formatear y calcular indicadores económicos colombianos.
"""

from __future__ import annotations

from typing import Optional, Union


def formatear_pesos(
    valor: Union[int, float],
    decimales: int = 0,
    abreviar: bool = False,
) -> str:
    """
    Formatea un valor numérico como pesos colombianos (COP).

    Parámetros
    ----------
    valor : int or float
        Monto en pesos colombianos.
    decimales : int
        Número de decimales a mostrar. Por defecto 0.
    abreviar : bool
        Si True, abrevia grandes valores (M = millones, B = billones).

    Retorna
    -------
    str
        Cadena formateada como peso colombiano.

    Ejemplo
    -------
    >>> from colombia_data.utils import formatear_pesos
    >>> formatear_pesos(1_500_000)
    '$1.500.000'
    >>> formatear_pesos(2_300_000_000, abreviar=True)
    '$2.300 M'
    """
    if abreviar:
        if abs(valor) >= 1_000_000_000_000:
            return f"${valor / 1_000_000_000_000:,.{decimales}f} B".replace(",", ".")
        elif abs(valor) >= 1_000_000:
            return f"${valor / 1_000_000:,.{decimales}f} M".replace(",", ".")
        elif abs(valor) >= 1_000:
            return f"${valor / 1_000:,.{decimales}f} K".replace(",", ".")

    # Formato con separador de miles colombiano (punto) y decimal (coma)
    if decimales > 0:
        resultado = f"{valor:,.{decimales}f}"
        # Intercambiar separadores: coma→punto, punto→coma
        resultado = resultado.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        resultado = f"{int(round(valor)):,}".replace(",", ".")

    return f"${resultado}"


def calcular_poder_adquisitivo(
    salario_actual: float,
    inflacion_acumulada_pct: float,
) -> dict:
    """
    Calcula el poder adquisitivo real dado un salario y la inflación acumulada.

    Parámetros
    ----------
    salario_actual : float
        Salario nominal actual en pesos colombianos.
    inflacion_acumulada_pct : float
        Inflación acumulada en el período (porcentaje, ej: 25.3 para 25.3%).

    Retorna
    -------
    dict
        Diccionario con:
        - salario_nominal: valor original
        - salario_real: valor a precios constantes
        - perdida_poder_adquisitivo_pct: porcentaje de pérdida
        - se_necesita_para_mantener: salario necesario para mantener poder adquisitivo

    Ejemplo
    -------
    >>> from colombia_data.utils import calcular_poder_adquisitivo
    >>> resultado = calcular_poder_adquisitivo(3_500_000, 45.2)
    >>> print(f"Pérdida de poder adquisitivo: {resultado['perdida_poder_adquisitivo_pct']:.1f}%")
    """
    factor = 1 + inflacion_acumulada_pct / 100
    salario_real = salario_actual / factor
    perdida_pct = ((salario_actual - salario_real) / salario_actual) * 100
    salario_necesario = salario_actual * factor

    return {
        "salario_nominal": round(salario_actual, 2),
        "salario_real": round(salario_real, 2),
        "perdida_poder_adquisitivo_pct": round(perdida_pct, 2),
        "se_necesita_para_mantener": round(salario_necesario, 2),
    }


def smmlv_a_usd(
    smmlv: float,
    trm: float,
    anios_smmlv: Optional[int] = None,
) -> dict:
    """
    Convierte el Salario Mínimo Mensual Legal Vigente (SMMLV) a dólares.

    Parámetros
    ----------
    smmlv : float
        Valor del SMMLV en pesos colombianos.
    trm : float
        Tasa Representativa del Mercado (COP por USD).
    anios_smmlv : int, opcional
        Número de SMMLV a convertir. Por defecto 1.

    Retorna
    -------
    dict
        Conversión con smmlv_cop, trm_usada, smmlv_usd.

    Ejemplo
    -------
    >>> from colombia_data.utils import smmlv_a_usd
    >>> resultado = smmlv_a_usd(1_300_000, 4_050)
    >>> print(f"SMMLV en USD: ${resultado['smmlv_usd']:.0f}")
    """
    n = anios_smmlv or 1
    total_cop = smmlv * n
    total_usd = total_cop / trm

    return {
        "smmlv_cop": round(total_cop, 2),
        "trm_usada": round(trm, 2),
        "smmlv_usd": round(total_usd, 2),
    }


def calcular_retencion_simple(ingreso: float, uvt: float = 47065.0) -> dict:
    """
    Calcula una retención en la fuente simplificada para rentas de trabajo.

    Basado en el Estatuto Tributario colombiano Art. 383.
    Nota: para retenciones por honorarios usar el módulo factura_co.

    Parámetros
    ----------
    ingreso : float
        Ingreso mensual bruto en pesos colombianos.
    uvt : float
        Valor de la UVT vigente. Por defecto 47.065 (UVT 2024).

    Retorna
    -------
    dict
        ingreso_bruto, ingreso_en_uvt, retencion_cop, ingreso_neto.
    """
    ingreso_uvt = ingreso / uvt

    # Tabla de retención simplificada Art. 383 ET
    if ingreso_uvt < 95:
        tasa = 0.0
    elif ingreso_uvt < 150:
        tasa = 0.19
    elif ingreso_uvt < 360:
        tasa = 0.28
    elif ingreso_uvt < 640:
        tasa = 0.33
    elif ingreso_uvt < 945:
        tasa = 0.35
    elif ingreso_uvt < 2300:
        tasa = 0.37
    else:
        tasa = 0.39

    retencion = ingreso * tasa

    return {
        "ingreso_bruto": round(ingreso, 0),
        "ingreso_en_uvt": round(ingreso_uvt, 2),
        "tasa_marginal_pct": round(tasa * 100, 1),
        "retencion_cop": round(retencion, 0),
        "ingreso_neto": round(ingreso - retencion, 0),
    }
