# 🇨🇴 Colombia Data Insights

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-orange?logo=jupyter)](notebooks/)
[![Fuente: DANE](https://img.shields.io/badge/Fuente-DANE-red)](https://www.dane.gov.co/)
[![Fuente: Banrep](https://img.shields.io/badge/Fuente-Banco%20de%20la%20Rep%C3%BAblica-yellow)](https://www.banrep.gov.co/)

> **Análisis de datos públicos colombianos** — inflación, mercado laboral, economía y más.  
> Datos reales de fuentes oficiales (DANE, Banco de la República) procesados con Python.

---

## 📋 Tabla de Contenidos

1. [Descripción](#-descripción)
2. [Notebooks disponibles](#-notebooks-disponibles)
3. [Estructura del proyecto](#-estructura-del-proyecto)
4. [Instalación](#-instalación)
5. [Uso rápido](#-uso-rápido)
6. [Fuentes de datos](#-fuentes-de-datos)
7. [Contribuir](#-contribuir)
8. [Licencia](#-licencia)

---

## 📊 Descripción

Este repositorio reúne análisis exploratorios y visualizaciones de datos públicos colombianos con el objetivo de:

- **Entender la economía colombiana** a través de sus principales indicadores
- **Democratizar el acceso** a datos oficiales con código reutilizable
- **Servir como portafolio** de ciencia de datos aplicada al contexto colombiano

Los análisis están escritos en **español**, orientados a audiencias técnicas y no técnicas.

---

## 📓 Notebooks disponibles

| Notebook | Descripción | Fuente |
|----------|-------------|--------|
| [01 — Exploración Inflación 2020–2024](notebooks/01_exploracion_inflacion.ipynb) | Análisis histórico del IPC, pandemia y pico inflacionario de 2022 | DANE / Banco de la República |
| *(próximamente)* Índices de Precios Productor | IPP vs IPC, transmisión de precios | DANE |
| [02 — Mercado Laboral 2015–2024](notebooks/02_mercado_laboral_colombiano.ipynb) | Desempleo trimestral, comparación por ciudad, impacto pandemia | DANE GEIH |

---

## 🗂 Estructura del proyecto

```
colombia-data-insights/
├── README.md                          # Este archivo
├── LICENSE                            # MIT License
├── requirements.txt                   # Dependencias Python
├── setup.py                           # Configuración del paquete
├── .gitignore
│
├── data/
│   ├── raw/                           # Datos originales sin procesar
│   └── processed/                     # Datos limpios y transformados
│
├── notebooks/
│   ├── 01_exploracion_inflacion.ipynb # Análisis de inflación colombiana
│   └── 02_mercado_laboral_colombiano.ipynb # Mercado laboral y desempleo
│
├── src/
│   └── colombia_data/
│       ├── __init__.py
│       └── fetcher.py                 # Clientes para APIs de DANE y Banrep
│
├── docs/
│   └── fuentes.md                     # Documentación de fuentes de datos
│
└── assets/                            # Imágenes y gráficas exportadas
```

---

## ⚙️ Instalación

**Requisitos:** Python 3.9+

```bash
# Clonar el repositorio
git clone https://github.com/Brausin/colombia-data-insights.git
cd colombia-data-insights

# Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete en modo desarrollo
pip install -e .
```

---

## 🚀 Uso rápido

### Obtener datos de inflación

```python
from colombia_data import BancoRepublicaClient

cliente = BancoRepublicaClient()

# Serie IPC 2020–2024
ipc = cliente.obtener_ipc(anio_inicio=2020, anio_fin=2024)
print(ipc.head(10))

#         fecha  variacion_anual  anio  mes
# 0  2020-01-01             3.62  2020    1
# 1  2020-02-01             3.72  2020    2
# ...
```

### Obtener datos de desempleo

```python
from colombia_data import DANEClient

dane = DANEClient()
desempleo = dane.obtener_desempleo(anio_inicio=2020, anio_fin=2024)
print(desempleo)
```

### Abrir notebooks

```bash
jupyter notebook notebooks/
```

---

## 📚 Fuentes de datos

| Entidad | Descripción | Enlace |
|---------|-------------|--------|
| **DANE** | Estadísticas oficiales — IPC, desempleo, PIB | [dane.gov.co](https://www.dane.gov.co/) |
| **Banco de la República** | Política monetaria, inflación, tasa de cambio | [banrep.gov.co](https://www.banrep.gov.co/) |
| **Datos Abiertos Colombia** | Portal de datos del Gobierno Nacional | [datos.gov.co](https://www.datos.gov.co/) |
| **Ministerio de Hacienda** | Presupuesto público, deuda | [minhacienda.gov.co](https://www.minhacienda.gov.co/) |

Ver documentación completa en [`docs/fuentes.md`](docs/fuentes.md).

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Para contribuir:

1. Haz un fork del repositorio
2. Crea una rama: `git checkout -b feature/mi-analisis`
3. Agrega tu análisis o mejora con documentación en español
4. Abre un Pull Request describiendo qué datos analizas y por qué son relevantes

Por favor mantén el estándar del código: docstrings en español, type hints, y notebooks con markdown explicativo.

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para detalles.

---

<p align="center">
  Hecho con ❤️ para entender mejor a Colombia 🇨🇴
</p>
