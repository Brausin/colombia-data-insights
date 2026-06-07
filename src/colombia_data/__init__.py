"""
colombia_data
=============
Módulo para obtener y procesar datos públicos colombianos
desde fuentes oficiales como DANE y Banco de la República.
"""

__version__ = "0.1.0"
__author__ = "Brausin"

from .fetcher import BancoRepublicaClient, DANEClient

__all__ = ["BancoRepublicaClient", "DANEClient"]
