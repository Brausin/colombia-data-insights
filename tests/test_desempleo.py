"""
tests/test_desempleo.py
=======================
Suite de tests para el módulo colombia_data.desempleo.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from colombia_data.desempleo import (
    CIUDADES_DISPONIBLES,
    _normalizar_ciudad,
    comparar_ciudades,
    get_desempleo,
    promedio_anual,
)


# ---------------------------------------------------------------------------
# Tests: get_desempleo()
# ---------------------------------------------------------------------------


class TestGetDesempleo:
    def test_retorna_dataframe(self):
        df = get_desempleo()
        assert isinstance(df, pd.DataFrame)

    def test_columnas_requeridas_nacional(self):
        df = get_desempleo()
        assert "año" in df.columns
        assert "trimestre" in df.columns
        assert "periodo" in df.columns
        assert "tasa_desempleo" in df.columns

    def test_columnas_requeridas_ciudad(self):
        df = get_desempleo(ciudad="bogota")
        assert "año" in df.columns
        assert "tasa_desempleo" in df.columns

    def test_rango_anos_correcto(self):
        df = get_desempleo(anio_inicio=2020, anio_fin=2022)
        assert df["año"].min() >= 2020
        assert df["año"].max() <= 2022

    def test_dataset_completo_tiene_40_filas(self):
        # 10 años × 4 trimestres = 40 registros
        df = get_desempleo()
        assert len(df) == 40

    def test_tasas_positivas(self):
        df = get_desempleo()
        assert (df["tasa_desempleo"] > 0).all()

    def test_tasas_en_rango_plausible(self):
        # Entre 5% y 30% para Colombia (2015-2024)
        df = get_desempleo()
        assert df["tasa_desempleo"].min() >= 5
        assert df["tasa_desempleo"].max() <= 30

    def test_pico_covid_2020_t2(self):
        # El desempleo nacional llegó a ~21% en 2020-T2 por el COVID
        df = get_desempleo(anio_inicio=2020, anio_fin=2020)
        t2 = df[df["trimestre"] == 2]["tasa_desempleo"].values
        assert len(t2) > 0
        assert t2[0] > 15, "El pico de 2020-T2 debería superar el 15%"

    def test_ciudad_bogota_sin_tilde(self):
        df = get_desempleo(ciudad="bogota")
        assert not df.empty

    def test_ciudad_bogota_con_tilde(self):
        df = get_desempleo(ciudad="Bogotá")
        assert not df.empty

    def test_ciudad_case_insensitive(self):
        df1 = get_desempleo(ciudad="BOGOTA")
        df2 = get_desempleo(ciudad="bogota")
        pd.testing.assert_frame_equal(df1, df2)

    def test_ciudad_invalida_lanza_error(self):
        with pytest.raises(ValueError, match="no encontrada"):
            get_desempleo(ciudad="PaisQueNoExiste")

    def test_medellin_con_tilde(self):
        df = get_desempleo(ciudad="Medellín")
        assert not df.empty

    def test_datos_ciudad_difieren_de_nacional(self):
        df_nac = get_desempleo()
        df_bog = get_desempleo(ciudad="bogota")
        # Los valores deben ser distintos (Bogotá ≠ promedio nacional)
        assert not df_nac["tasa_desempleo"].equals(df_bog["tasa_desempleo"])


# ---------------------------------------------------------------------------
# Tests: comparar_ciudades()
# ---------------------------------------------------------------------------


class TestCompararCiudades:
    def test_retorna_dataframe(self):
        result = comparar_ciudades(["bogota", "medellin"], 2023)
        assert isinstance(result, pd.DataFrame)

    def test_columnas_correctas(self):
        result = comparar_ciudades(["bogota", "cali"], 2022)
        assert "ciudad" in result.columns
        assert "tasa_desempleo_pct" in result.columns

    def test_cantidad_filas_igual_a_ciudades(self):
        ciudades = ["bogota", "medellin", "cali", "barranquilla"]
        result = comparar_ciudades(ciudades, 2023)
        assert len(result) == len(ciudades)

    def test_ordenado_de_menor_a_mayor(self):
        result = comparar_ciudades(["bogota", "medellin", "ibague"], 2023)
        tasas = result["tasa_desempleo_pct"].tolist()
        assert tasas == sorted(tasas), "Debería estar ordenado de menor a mayor"

    def test_tasas_positivas(self):
        result = comparar_ciudades(["bogota", "cali"], 2022)
        assert (result["tasa_desempleo_pct"] > 0).all()

    def test_tasas_en_rango_plausible(self):
        result = comparar_ciudades(["bogota", "medellin", "cali"], 2023)
        assert result["tasa_desempleo_pct"].min() >= 5
        assert result["tasa_desempleo_pct"].max() <= 30

    def test_ibague_suele_tener_desempleo_alto(self):
        # Ibagué históricamente tiene desempleo alto (>12%)
        result = comparar_ciudades(["bogota", "ibague"], 2023)
        ibague_tasa = result[result["ciudad"] == "ibague"]["tasa_desempleo_pct"].values[0]
        bogota_tasa = result[result["ciudad"] == "bogota"]["tasa_desempleo_pct"].values[0]
        assert ibague_tasa > bogota_tasa, "Ibagué suele superar a Bogotá en desempleo"

    def test_ciudad_invalida_lanza_error(self):
        with pytest.raises(ValueError, match="no encontrada"):
            comparar_ciudades(["bogota", "ciudadinventada"], 2023)

    def test_ano_fuera_de_rango_lanza_error(self):
        with pytest.raises(ValueError, match="No hay datos para el año"):
            comparar_ciudades(["bogota", "medellin"], 1990)

    def test_acepta_nombres_con_tilde(self):
        result = comparar_ciudades(["Bogotá", "Medellín", "Cali"], 2023)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# Tests: promedio_anual()
# ---------------------------------------------------------------------------


class TestPromedioAnual:
    def test_retorna_dataframe(self):
        result = promedio_anual()
        assert isinstance(result, pd.DataFrame)

    def test_columnas_correctas(self):
        result = promedio_anual()
        assert "anio" in result.columns
        assert "tasa_desempleo_promedio_pct" in result.columns

    def test_cubre_anos_del_dataset(self):
        result = promedio_anual()
        assert result["anio"].min() <= 2015
        assert result["anio"].max() >= 2024

    def test_pico_2020_por_covid(self):
        result = promedio_anual()
        tasa_2020 = result[result["anio"] == 2020]["tasa_desempleo_promedio_pct"].values[0]
        tasa_2019 = result[result["anio"] == 2019]["tasa_desempleo_promedio_pct"].values[0]
        assert tasa_2020 > tasa_2019 + 3, "2020 debería tener desempleo mucho mayor por COVID"

    def test_recuperacion_post_covid(self):
        result = promedio_anual()
        tasa_2021 = result[result["anio"] == 2021]["tasa_desempleo_promedio_pct"].values[0]
        tasa_2023 = result[result["anio"] == 2023]["tasa_desempleo_promedio_pct"].values[0]
        assert tasa_2023 < tasa_2021, "Para 2023 el desempleo debería haber bajado vs 2021"

    def test_valores_positivos(self):
        result = promedio_anual()
        assert (result["tasa_desempleo_promedio_pct"] > 0).all()

    def test_ciudad_bogota(self):
        result = promedio_anual(ciudad="bogota")
        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_ciudad_bogota_con_tilde(self):
        result = promedio_anual(ciudad="Bogotá")
        assert not result.empty

    def test_ciudad_vs_nacional_difieren(self):
        nac = promedio_anual()
        bog = promedio_anual("bogota")
        # Las tasas no deben ser idénticas
        tasas_nac = set(nac["tasa_desempleo_promedio_pct"].tolist())
        tasas_bog = set(bog["tasa_desempleo_promedio_pct"].tolist())
        assert tasas_nac != tasas_bog

    def test_ciudad_invalida_lanza_error(self):
        with pytest.raises(ValueError, match="no encontrada"):
            promedio_anual(ciudad="CiudadFalsa")


# ---------------------------------------------------------------------------
# Tests: _normalizar_ciudad() y CIUDADES_DISPONIBLES
# ---------------------------------------------------------------------------


class TestNormalizarCiudad:
    def test_bogota_sin_tilde(self):
        assert _normalizar_ciudad("bogota") == "bogota"

    def test_bogota_con_tilde(self):
        assert _normalizar_ciudad("Bogotá") == "bogota"

    def test_medellin_con_tilde(self):
        assert _normalizar_ciudad("Medellín") == "medellin"

    def test_case_insensitive(self):
        assert _normalizar_ciudad("CALI") == "cali"
        assert _normalizar_ciudad("Cali") == "cali"

    def test_ciudad_invalida_retorna_none(self):
        assert _normalizar_ciudad("Londres") is None

    def test_todas_ciudades_disponibles_se_normalizan(self):
        for ciudad in CIUDADES_DISPONIBLES:
            resultado = _normalizar_ciudad(ciudad)
            assert resultado is not None, f"Falló para: {ciudad}"


class TestCiudadesDisponibles:
    def test_al_menos_10_ciudades(self):
        assert len(CIUDADES_DISPONIBLES) >= 10

    def test_incluye_principales_ciudades(self):
        principales = {"bogota", "medellin", "cali", "barranquilla"}
        assert principales.issubset(set(CIUDADES_DISPONIBLES))
