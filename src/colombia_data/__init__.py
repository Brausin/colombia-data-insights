"""
colombia_data
=============
Librería Python para acceder y analizar datos económicos de Colombia.

Fuentes: DANE, Banco de la República

Módulos disponibles
-------------------
- ipc         : Índice de Precios al Consumidor
- desempleo   : Mercado laboral y tasas de desempleo
- exportaciones: Comercio exterior colombiano
- utils       : Utilidades de formato y cálculo

Ejemplo rápido
--------------
>>> from colombia_data.ipc import get_ipc, ajustar_por_inflacion
>>> df = get_ipc(2020, 2024)
>>> print(df.tail())

>>> from colombia_data.utils import smmlv, formatear_pesos
>>> print(formatear_pesos(smmlv(2024)))
'$ 1.300.000'
"""

__version__ = "0.2.0"
__author__ = "Brausin"

from .fetcher import BancoRepublicaClient, DANEClient
from .ipc import get_ipc, variacion_ipc, ajustar_por_inflacion
from .desempleo import get_desempleo, comparar_ciudades
from .exportaciones import get_exportaciones, top_productos
from .utils import formatear_pesos, calcular_poder_adquisitivo, smmlv, uvt

__all__ = [
    "BancoRepublicaClient",
    "DANEClient",
    "get_ipc",
    "variacion_ipc",
    "ajustar_por_inflacion",
    "get_desempleo",
    "comparar_ciudades",
    "get_exportaciones",
    "top_productos",
    "formatear_pesos",
    "calcular_poder_adquisitivo",
    "smmlv",
    "uvt",
]
