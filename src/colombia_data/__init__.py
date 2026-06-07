"""
colombia_data
=============
Librería Python para acceder y analizar datos económicos públicos de Colombia.

Módulos disponibles
-------------------
- ipc        : Índice de Precios al Consumidor (inflación)
- desempleo  : Mercado laboral y tasas de desempleo
- exportaciones : Exportaciones por producto y destino
- trm        : Tasa Representativa del Mercado (USD/COP)
- utils      : Utilidades: formateo de pesos, poder adquisitivo, retenciones

Fuentes: DANE, Banco de la República de Colombia.
"""

__version__ = "0.2.0"
__author__ = "Brausin"

from .fetcher import BancoRepublicaClient, DANEClient
from .ipc import get_ipc, variacion_ipc, ajustar_por_inflacion
from .exportaciones import get_exportaciones, top_productos, evolucion_producto, total_por_anio
from .desempleo import get_desempleo, comparar_ciudades, promedio_anual
from .utils import formatear_pesos, calcular_poder_adquisitivo, smmlv_a_usd, calcular_retencion_simple

__all__ = [
    # Clientes
    "BancoRepublicaClient",
    "DANEClient",
    # IPC
    "get_ipc",
    "variacion_ipc",
    "ajustar_por_inflacion",
    # Exportaciones
    "get_exportaciones",
    "top_productos",
    "evolucion_producto",
    "total_por_anio",
    # Desempleo
    "get_desempleo",
    "comparar_ciudades",
    "promedio_anual",
    # Utils
    "formatear_pesos",
    "calcular_poder_adquisitivo",
    "smmlv_a_usd",
    "calcular_retencion_simple",
]
