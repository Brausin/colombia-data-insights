"""Tests para el módulo exportaciones.py."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from colombia_data.exportaciones import get_exportaciones, top_productos


def test_get_exportaciones_retorna_dataframe():
    df = get_exportaciones(2020, 2024)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_get_exportaciones_rango_correcto():
    df = get_exportaciones(2020, 2022)
    assert df["anio"].min() >= 2020
    assert df["anio"].max() <= 2022


def test_get_exportaciones_filtro_sector():
    df = get_exportaciones(2020, 2024, sector="Minería")
    assert (df["sector"] == "Minería").all()


def test_get_exportaciones_sector_invalido():
    with pytest.raises(ValueError):
        get_exportaciones(2020, 2024, sector="Tecnología")


def test_top_productos_retorna_n_filas():
    top = top_productos(2024, n=5)
    assert len(top) == 5


def test_top_productos_orden_descendente():
    top = top_productos(2024, n=5)
    valores = top["valor_millones_usd"].tolist()
    assert valores == sorted(valores, reverse=True)


def test_top_productos_columnas():
    top = top_productos(2024)
    for col in ["producto", "sector", "valor_millones_usd"]:
        assert col in top.columns


def test_top_productos_anio_invalido():
    with pytest.raises(ValueError):
        top_productos(1900)
