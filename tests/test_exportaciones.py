"""
Pruebas para el módulo de exportaciones colombianas.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from colombia_data.exportaciones import (
    get_exportaciones,
    top_productos,
    evolucion_producto,
    total_por_anio,
)


class TestGetExportaciones:
    def test_retorna_dataframe(self):
        df = get_exportaciones()
        assert isinstance(df, pd.DataFrame)

    def test_filtra_por_anios(self):
        df = get_exportaciones(anio_inicio=2018, anio_fin=2020)
        assert df["anio"].min() >= 2018
        assert df["anio"].max() <= 2020

    def test_filtra_por_producto(self):
        df = get_exportaciones(producto="Cafe")
        assert all(df["producto"].str.contains("Cafe", case=False))

    def test_columnas_requeridas(self):
        df = get_exportaciones()
        columnas_esperadas = ["anio", "producto", "valor_millones_usd", "participacion_pct"]
        for col in columnas_esperadas:
            assert col in df.columns, f"Falta columna: {col}"

    def test_valores_positivos(self):
        df = get_exportaciones()
        assert (df["valor_millones_usd"] > 0).all()

    def test_participacion_entre_0_y_100(self):
        df = get_exportaciones()
        assert (df["participacion_pct"] >= 0).all()
        assert (df["participacion_pct"] <= 100).all()


class TestTopProductos:
    def test_retorna_n_productos(self):
        resultado = top_productos(n=3)
        assert len(resultado) == 3

    def test_retorna_dataframe(self):
        resultado = top_productos()
        assert isinstance(resultado, pd.DataFrame)

    def test_filtro_por_anio(self):
        resultado = top_productos(anio=2024, n=5)
        assert len(resultado) <= 5

    def test_petroleo_entre_top_exportaciones(self):
        """El petróleo históricamente es el mayor producto de exportación."""
        resultado = top_productos(n=3)
        productos = resultado.iloc[:, 0].str.lower().tolist()
        assert any("petroleo" in p or "petróleo" in p for p in productos)


class TestEvolucionProducto:
    def test_serie_historica_cafe(self):
        df = evolucion_producto("Cafe")
        assert len(df) > 5
        assert "anio" in df.columns
        assert "valor_millones_usd" in df.columns

    def test_todos_anios_cubiertos(self):
        df = evolucion_producto("Carbon")
        assert df["anio"].min() <= 2015
        assert df["anio"].max() >= 2022


class TestTotalPorAnio:
    def test_retorna_totales_anuales(self):
        df = total_por_anio()
        assert "anio" in df.columns
        assert "total_millones_usd" in df.columns

    def test_auge_petroleo_2012(self):
        """Entre 2011-2014 Colombia tuvo su mayor auge exportador por petróleo."""
        df = total_por_anio(anio_inicio=2010, anio_fin=2016)
        idx_max = df["total_millones_usd"].idxmax()
        anio_pico = df.loc[idx_max, "anio"]
        assert 2011 <= anio_pico <= 2014

    def test_caida_2015_por_petroleo(self):
        """La caída del precio del petróleo en 2015 redujo exportaciones."""
        df = total_por_anio(anio_inicio=2014, anio_fin=2016)
        total_2014 = df[df["anio"] == 2014]["total_millones_usd"].values[0]
        total_2015 = df[df["anio"] == 2015]["total_millones_usd"].values[0]
        assert total_2015 < total_2014
