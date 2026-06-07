"""Tests para el módulo ipc.py."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from colombia_data.ipc import get_ipc, variacion_ipc, ajustar_por_inflacion


def test_get_ipc_retorna_dataframe():
    df = get_ipc(2022, 2024)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_get_ipc_columnas_minimas():
    df = get_ipc(2022, 2024)
    assert "variacion_anual" in df.columns
    assert any(c in df.columns for c in ["año", "anio", "year"])


def test_get_ipc_rango_correcto():
    df = get_ipc(2022, 2023)
    col_anio = next(c for c in df.columns if c in ("año", "anio", "year"))
    assert df[col_anio].min() >= 2022
    assert df[col_anio].max() <= 2023


def test_get_ipc_valores_altos_en_2022():
    df = get_ipc(2022, 2022)
    # En 2022 la inflación colombiana superó el 6%
    assert df["variacion_anual"].mean() > 6.0


def test_variacion_ipc_retorna_float():
    # variacion_ipc retorna la variación acumulada en % como float
    var = variacion_ipc(2022, 2024)
    assert isinstance(var, (float, int))
    assert var > 0


def test_variacion_ipc_rango_valido():
    # Inflación acumulada 2021-2023 fue considerable (>20%)
    var = variacion_ipc(2021, 2023)
    assert var > 20.0


def test_ajustar_por_inflacion_igual_anio():
    resultado = ajustar_por_inflacion(1_000_000, 2022, 2022)
    assert resultado == 1_000_000.0


def test_ajustar_por_inflacion_hacia_adelante():
    # 1M de 2020 debe valer más en 2024 (inflación acumulada alta)
    resultado = ajustar_por_inflacion(1_000_000, 2020, 2024)
    assert resultado > 1_000_000


def test_ajustar_por_inflacion_hacia_atras():
    # 1M de 2024 debe equivaler a menos en 2020
    resultado = ajustar_por_inflacion(1_000_000, 2024, 2020)
    assert resultado < 1_000_000
