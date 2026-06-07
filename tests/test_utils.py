"""
Pruebas para funciones utilitarias del módulo colombia_data.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from colombia_data.utils import (
    formatear_pesos,
    calcular_poder_adquisitivo,
    smmlv_a_usd,
    calcular_retencion_simple,
)


class TestFormatearPesos:
    def test_formato_basico(self):
        assert formatear_pesos(1000) == "$1.000"

    def test_formato_millon(self):
        assert formatear_pesos(1_500_000) == "$1.500.000"

    def test_formato_abreviado_millones(self):
        resultado = formatear_pesos(2_300_000, abreviar=True)
        assert "M" in resultado
        assert "$" in resultado

    def test_formato_abreviado_billones(self):
        resultado = formatear_pesos(5_000_000_000_000, abreviar=True)
        assert "B" in resultado

    def test_cero(self):
        assert formatear_pesos(0) == "$0"

    def test_valor_negativo(self):
        resultado = formatear_pesos(-500_000)
        assert "$" in resultado

    def test_con_decimales(self):
        resultado = formatear_pesos(1_234_567.89, decimales=2)
        assert "$" in resultado


class TestCalcularPoderAdquisitivo:
    def test_estructura_retorno(self):
        resultado = calcular_poder_adquisitivo(3_000_000, 30.0)
        assert "salario_nominal" in resultado
        assert "salario_real" in resultado
        assert "perdida_poder_adquisitivo_pct" in resultado
        assert "se_necesita_para_mantener" in resultado

    def test_sin_inflacion(self):
        resultado = calcular_poder_adquisitivo(2_000_000, 0.0)
        assert resultado["salario_real"] == 2_000_000
        assert resultado["perdida_poder_adquisitivo_pct"] == 0.0

    def test_inflacion_positiva_reduce_poder(self):
        resultado = calcular_poder_adquisitivo(2_000_000, 20.0)
        assert resultado["salario_real"] < 2_000_000
        assert resultado["perdida_poder_adquisitivo_pct"] > 0

    def test_salario_necesario_mayor(self):
        resultado = calcular_poder_adquisitivo(3_000_000, 15.0)
        assert resultado["se_necesita_para_mantener"] > 3_000_000


class TestSmmlvAUsd:
    def test_conversion_basica(self):
        resultado = smmlv_a_usd(1_300_000, 4_000)
        assert resultado["smmlv_usd"] == pytest.approx(325.0, rel=0.01)

    def test_estructura_retorno(self):
        resultado = smmlv_a_usd(1_300_000, 4_000)
        assert "smmlv_cop" in resultado
        assert "trm_usada" in resultado
        assert "smmlv_usd" in resultado

    def test_multiples_smmlv(self):
        resultado = smmlv_a_usd(1_300_000, 4_000, anios_smmlv=2)
        assert resultado["smmlv_cop"] == 2_600_000


class TestCalcularRetencionSimple:
    def test_sin_retencion_ingresos_bajos(self):
        """Ingresos por debajo de 95 UVT no tienen retención."""
        # 95 UVT = 95 * 47.065 = ~4.471.175 pesos
        resultado = calcular_retencion_simple(3_000_000)
        assert resultado["retencion_cop"] == 0

    def test_retencion_positiva_ingresos_altos(self):
        resultado = calcular_retencion_simple(15_000_000)
        assert resultado["retencion_cop"] > 0

    def test_ingreso_neto_menor_bruto(self):
        resultado = calcular_retencion_simple(15_000_000)
        assert resultado["ingreso_neto"] < resultado["ingreso_bruto"]

    def test_estructura_retorno(self):
        resultado = calcular_retencion_simple(10_000_000)
        assert "ingreso_bruto" in resultado
        assert "ingreso_en_uvt" in resultado
        assert "tasa_marginal_pct" in resultado
        assert "retencion_cop" in resultado
        assert "ingreso_neto" in resultado

    def test_uvt_personalizado(self):
        uvt_2023 = 42412.0
        resultado = calcular_retencion_simple(10_000_000, uvt=uvt_2023)
        assert resultado["ingreso_en_uvt"] == pytest.approx(10_000_000 / uvt_2023, rel=0.01)
