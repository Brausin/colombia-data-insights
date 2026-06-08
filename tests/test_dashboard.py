"""
tests/test_dashboard.py
=======================
Pruebas de regresión para el dashboard (app/main.py).

Cubren dos riesgos que en el pasado dejaron la app inservible:

1. **Contratos de datos**: que las funciones de la librería sigan devolviendo
   las columnas y claves que el dashboard espera. Si alguien renombra una
   columna del CSV o cambia una firma, estas pruebas fallan antes de romper
   la app en producción.
2. **Smoke test de la app**: que `app/main.py` se ejecute de principio a fin
   sin lanzar excepciones (todas las pestañas se renderizan en una corrida).
"""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "src"))

from colombia_data.ipc import get_ipc
from colombia_data.desempleo import get_desempleo, comparar_ciudades, CIUDADES_DISPONIBLES
from colombia_data.exportaciones import get_exportaciones, top_productos
from colombia_data.utils import calcular_poder_adquisitivo, smmlv_a_usd


# ── Contratos de datos que el dashboard consume ──────────────────────────────

def test_ipc_columnas_esperadas():
    df = get_ipc()
    for col in ("año", "mes", "periodo", "ipc", "variacion_anual"):
        assert col in df.columns, f"IPC sin columna '{col}'"
    assert len(df) > 0


def test_desempleo_columnas_esperadas():
    df = get_desempleo()
    for col in ("periodo", "tasa_desempleo"):
        assert col in df.columns, f"Desempleo sin columna '{col}'"
    assert len(df) > 0


def test_exportaciones_columna_valor():
    df = get_exportaciones()
    assert "valor_millones_usd" in df.columns
    assert "producto" in df.columns and "anio" in df.columns


def test_top_productos_contrato():
    anio = int(get_exportaciones()["anio"].max())
    top = top_productos(anio=anio, n=8)
    assert list(top.columns) == ["producto", "valor_millones_usd"] or {
        "producto", "valor_millones_usd"
    }.issubset(top.columns)
    assert len(top) > 0


def test_producto_petroleo_existe_con_nombre_exacto():
    # El dashboard filtra por este nombre exacto (sin tilde).
    productos = set(get_exportaciones()["producto"].unique())
    assert "Petroleo y derivados" in productos


def test_smmlv_a_usd_clave():
    res = smmlv_a_usd(3_000_000, 4_100)
    assert "smmlv_usd" in res
    assert res["smmlv_usd"] == pytest.approx(3_000_000 / 4_100, rel=1e-3)


def test_poder_adquisitivo_claves():
    res = calcular_poder_adquisitivo(1_000_000, 35.0)
    for clave in ("salario_real", "se_necesita_para_mantener",
                  "perdida_poder_adquisitivo_pct"):
        assert clave in res


def test_comparar_ciudades_devuelve_tasa():
    df = comparar_ciudades(["bogota", "medellin", "cali"], 2023)
    assert "tasa_desempleo_pct" in df.columns
    assert "ciudad" in df.columns
    assert len(df) == 3


# ── Smoke test de la app completa ────────────────────────────────────────────

def test_dashboard_se_renderiza_sin_excepciones():
    """La app debe ejecutarse de punta a punta sin lanzar excepciones."""
    apptest = pytest.importorskip("streamlit.testing.v1")
    AppTest = apptest.AppTest

    at = AppTest.from_file(str(_REPO / "app" / "main.py"), default_timeout=120)
    at.run()

    assert at.exception is None or len(at.exception) == 0, (
        f"El dashboard lanzó una excepción: {at.exception}"
    )
    # Debe haber renderizado las 5 secciones principales.
    assert len(at.subheader) >= 5
    # Y no debe haber elementos de error en pantalla.
    assert len(at.error) == 0
