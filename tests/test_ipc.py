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


def test_get_ipc_columnas_esperadas():
    df = get_ipc(2022, 2024)
    for col in ["fecha", "variacion_anual", "anio", "mes"]:
        assert col in df.columns, f"Falta columna: {col}"


def test_get_ipc_rango_correcto():
    df = get_ipc(2022, 2023)
    assert df["anio"].min() >= 2022
    assert df["anio"].max() <= 2023


def test_get_ipc_valores_positivos_pos_pandemia():
    df = get_ipc(2022, 2022)
    # En 2022 la inflación en Colombia superó el 6%
    assert df["variacion_anual"].mean() > 6.0


def test_variacion_promedio_anual():
    df = get_ipc(2022, 2024)
    var = variacion_ipc(df, "promedio_anual")
    assert "ipc_promedio_anual" in var.columns
    assert len(var) == 3  # 2022, 2023, 2024


def test_variacion_periodo_invalido():
    df = get_ipc(2022, 2024)
    with pytest.raises(ValueError):
        variacion_ipc(df, "quincenal")


def test_ajustar_por_inflacion_igual_anio():
    resultado = ajustar_por_inflacion(1_000_000, 2022, 2022)
    assert resultado == 1_000_000.0


def test_ajustar_por_inflacion_hacia_adelante():
    # 1M de 2020 debe valer más en 2024 (inflación acumulada)
    resultado = ajustar_por_inflacion(1_000_000, 2020, 2024)
    assert resultado > 1_000_000


def test_ajustar_por_inflacion_hacia_atras():
    # 1M de 2024 debe equivaler a menos en 2020
    resultado = ajustar_por_inflacion(1_000_000, 2024, 2020)
    assert resultado < 1_000_000
