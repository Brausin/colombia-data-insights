"""
Tests del módulo trm_live: get_trm_hoy() y get_historico_trm().
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from colombia_data.trm_live import (
    get_trm_hoy,
    get_historico_trm,
    _trm_desde_respaldo,
    _trm_desde_csv,
)


class TestGetTrmHoy:
    """get_trm_hoy() siempre retorna un float positivo."""

    def test_retorna_float(self):
        trm = get_trm_hoy()
        assert isinstance(trm, float)

    def test_valor_positivo(self):
        trm = get_trm_hoy()
        assert trm > 0

    def test_rango_plausible_cop_usd(self):
        """TRM Colombia históricamente entre 1.500 y 6.000 COP/USD."""
        trm = get_trm_hoy()
        assert 1_500 <= trm <= 6_000, f"TRM fuera de rango plausible: {trm}"

    def test_no_lanza_excepcion_sin_api(self):
        """Incluso sin acceso a internet debe retornar valor."""
        trm = get_trm_hoy(timeout=1)
        assert trm > 0


class TestFallback:
    """El fallback interno retorna valores válidos."""

    def test_respaldo_retorna_float(self):
        trm = _trm_desde_respaldo()
        assert isinstance(trm, float)

    def test_respaldo_rango_plausible(self):
        trm = _trm_desde_respaldo()
        assert 3_000 <= trm <= 6_000

    def test_csv_retorna_none_si_no_existe(self, tmp_path, monkeypatch):
        """Cuando el CSV no existe, retorna None (no lanza excepción)."""
        import colombia_data.trm_live as tl
        monkeypatch.setattr(tl, "_CSV_PATH", tmp_path / "inexistente.csv")
        resultado = tl._trm_desde_csv()
        assert resultado is None


class TestHistoricoTrm:
    """get_historico_trm() retorna lista coherente."""

    def test_retorna_lista(self):
        hist = get_historico_trm(6)
        assert isinstance(hist, list)

    def test_longitud_correcta(self):
        hist = get_historico_trm(6)
        assert len(hist) == 6

    def test_estructura_items(self):
        hist = get_historico_trm(3)
        for item in hist:
            assert "fecha" in item
            assert "trm" in item

    def test_fechas_formato_anio_mes(self):
        hist = get_historico_trm(3)
        for item in hist:
            partes = item["fecha"].split("-")
            assert len(partes) == 2
            assert len(partes[0]) == 4  # YYYY
            assert len(partes[1]) == 2  # MM

    def test_valores_positivos(self):
        hist = get_historico_trm(12)
        for item in hist:
            assert item["trm"] > 0

    def test_orden_cronologico(self):
        hist = get_historico_trm(12)
        fechas = [item["fecha"] for item in hist]
        assert fechas == sorted(fechas)

    def test_meses_1_retorna_1(self):
        hist = get_historico_trm(1)
        assert len(hist) == 1

    def test_meses_por_defecto_12(self):
        hist = get_historico_trm()
        assert len(hist) == 12
