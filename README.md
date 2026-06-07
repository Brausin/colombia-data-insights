# 🇨🇴 Colombia Data Insights

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/Brausin/colombia-data-insights/actions)
[![Jupyter](https://img.shields.io/badge/Jupyter-6%20notebooks-orange?logo=jupyter)](notebooks/)

> Datos económicos colombianos — inflación, exportaciones, mercado laboral, tasa de cambio y costo de vida — accesibles con Python en un solo `pip install`.

¿Cuánto vale hoy un salario de 2018? ¿Qué tan caro es vivir en Bogotá vs Medellín? ¿Cómo cambiaron las exportaciones colombianas en la última década? Este proyecto responde esas preguntas con datos oficiales (DANE, Banco de la República) y código reproducible.

---

## ¿Qué incluye?

### Notebooks de análisis

| # | Notebook | Descripción |
|---|----------|-------------|
| 03 | [Tasa de Cambio USD/COP](notebooks/03_tasa_de_cambio.ipynb) | Evolución histórica del dólar, volatilidad y períodos de crisis cambiaria |
| 04 | [Exportaciones Colombia](notebooks/04_exportaciones_colombia.ipynb) | Principales productos exportados, destinos y tendencias por año |
| 05 | [Costo de Vida por Ciudades](notebooks/05_costo_de_vida_ciudades.ipynb) | Comparación del IPC entre Bogotá, Medellín, Cali, Barranquilla y otras ciudades |
| 06 | [Calculadora de Salario Real](notebooks/06_calculadora_salario_real.ipynb) | Ajuste de salarios por inflación: cuánto poder adquisitivo se ha ganado o perdido |
| 01 | [Exploración Inflación 2020–2024](notebooks/01_exploracion_inflacion.ipynb) | Análisis histórico del IPC y el pico inflacionario de 2022 |
| 02 | [Mercado Laboral 2015–2024](notebooks/02_mercado_laboral_colombiano.ipynb) | Desempleo trimestral y comparación por ciudad |

### Datasets disponibles

| Archivo | Descripción | Fuente |
|---------|-------------|--------|
| `data/processed/desempleo_colombia_2015_2024.csv` | Tasa de desempleo trimestral nacional y por ciudad | DANE GEIH |

Los datos en `data/raw/` se descargan automáticamente al ejecutar los notebooks o llamar a los clientes de la librería.

### Librería Python `colombia_data`

Módulos incluidos:

- **`ipc`** — IPC mensual, variación anual, ajuste de valores por inflación
- **`desempleo`** — Tasa de desempleo nacional y por ciudad desde 2015
- **`trm`** — Tasa Representativa del Mercado (USD/COP) histórica
- **`exportaciones`** — Exportaciones por producto, destino y año
- **`utils`** — Formateo de pesos colombianos, conversión a USD, cálculo de retenciones

---

## Instalación

**Requisitos:** Python 3.9+

```bash
git clone https://github.com/Brausin/colombia-data-insights.git
cd colombia-data-insights

# Entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

pip install -e .
```

---

## Ejemplos de uso

### Ajustar un salario por inflación

```python
from colombia_data import ajustar_por_inflacion, formatear_pesos

# ¿Cuánto equivale un salario de $3.000.000 de 2018 en pesos de 2024?
valor_actualizado = ajustar_por_inflacion(3_000_000, anio_origen=2018, anio_destino=2024)
print(formatear_pesos(valor_actualizado))
# → $ 5.241.300
```

### Obtener la TRM histórica

```python
from colombia_data import BancoRepublicaClient

cliente = BancoRepublicaClient()
trm = cliente.obtener_trm(anio_inicio=2020, anio_fin=2024)
print(trm.tail())
#          fecha      trm
# 1456 2024-12-27  4441.91
# 1457 2024-12-28  4441.91
```

### Comparar desempleo entre ciudades

```python
from colombia_data import comparar_ciudades

df = comparar_ciudades(["Bogotá", "Medellín", "Cali"], anio_inicio=2022, anio_fin=2024)
print(df.pivot(index="trimestre", columns="ciudad", values="tasa_desempleo"))
```

### Exportaciones: top productos

```python
from colombia_data import top_productos

productos = top_productos(anio=2023, n=10)
print(productos[["producto", "valor_usd_millones"]])
```

---

## Estructura del proyecto

```
colombia-data-insights/
├── notebooks/               # 6 análisis listos para ejecutar
│   ├── 01_exploracion_inflacion.ipynb
│   ├── 02_mercado_laboral_colombiano.ipynb
│   ├── 03_tasa_de_cambio.ipynb
│   ├── 04_exportaciones_colombia.ipynb
│   ├── 05_costo_de_vida_ciudades.ipynb
│   └── 06_calculadora_salario_real.ipynb
├── src/colombia_data/       # Librería instalable
│   ├── ipc.py
│   ├── desempleo.py
│   ├── trm.py
│   ├── exportaciones.py
│   ├── utils.py
│   └── fetcher.py           # Clientes para APIs de DANE y Banrep
├── data/
│   ├── raw/                 # Datos originales (ignorados por git)
│   └── processed/           # Datos limpios versionados
├── docs/                    # Documentación de fuentes y análisis
├── setup.py
└── requirements.txt
```

---

## Fuentes de datos

| Entidad | Datos | Enlace |
|---------|-------|--------|
| **DANE** | IPC, desempleo, exportaciones, costo de vida | [dane.gov.co](https://www.dane.gov.co/) |
| **Banco de la República** | TRM, tasas de interés, inflación | [banrep.gov.co](https://www.banrep.gov.co/) |
| **Datos Abiertos Colombia** | Conjuntos de datos del Gobierno Nacional | [datos.gov.co](https://www.datos.gov.co/) |

---

## Licencia

MIT — ver [LICENSE](LICENSE).

---

<p align="center">Hecho con ❤️ para entender mejor a Colombia 🇨🇴</p>
