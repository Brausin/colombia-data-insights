"""
colombia_data
=============
Módulo para obtener y procesar datos públicos colombianos
desde fuentes oficiales como DANE y Banco de la República.

Módulos disponibles:
- trm_live: TRM en tiempo real con fallback automático
- trm: análisis histórico TRM mensual
- ipc: inflación mensual histórica
- desempleo: tasa de desempleo trimestral
- exportaciones: exportaciones por producto
- utils: formateo y calculadoras financieras
"""

__version__ = "0.2.0"
__author__ = "Brausin"

from .fetcher import BancoRepublicaClient, DANEClient
from .trm_live import get_trm_hoy, get_historico_trm

__all__ = [
    "BancoRepublicaClient",
    "DANEClient",
    "get_trm_hoy",
    "get_historico_trm",
]
