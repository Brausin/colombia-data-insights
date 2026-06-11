<div align="center">

# 🇨🇴 Colombia Data Insights

*Los datos económicos públicos de Colombia, por fin usables: dashboard, librería y API REST.*

![Tests](https://img.shields.io/badge/tests-113%20passing-brightgreen?style=flat-square&logo=pytest)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![API](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)
![Fuente](https://img.shields.io/badge/datos-DANE%20%C2%B7%20BanRep%20%C2%B7%20Banco%20Mundial-yellow?style=flat-square)
![Actualización](https://img.shields.io/badge/actualizaci%C3%B3n-autom%C3%A1tica%20(Actions)-F59E0B?style=flat-square)

</div>

---

## El problema

Colombia publica una montaña de datos económicos —inflación del DANE, TRM del Banco de la República, exportaciones, desempleo, salario mínimo— pero viven dispersos en PDFs, anexos de Excel y portales lentos. Para responder algo tan simple como *"¿cuánto se devaluó el peso este año?"* o *"¿la inflación de 2023 superó la meta del Banco de la República?"* toca descargar planillas y pelear con ellas. **Colombia Data Insights** toma esas fuentes oficiales y las entrega de tres formas listas para usar: un **dashboard** interactivo, una **librería** de Python y una **API REST** pública.

## Dashboard

Construido en Streamlit con sistema de diseño **data-dense BI** (Fira Sans + Fira Code para cifras, encabezado con franja tricolor, KPIs con acento de color y gráficas Plotly en tema oscuro). Cada pestaña de datos permite **descargar la serie en CSV**:

| Pestaña | Qué muestra |
|---------|-------------|
| **TRM hoy** | Evolución del dólar con filtro de período (6/12/18/24 meses), marca del valor de hoy, conversor USD → COP en vivo y descarga del histórico. |
| **Inflación** | IPC mensual del DANE frente a la meta del 3 % del Banco de la República, más la serie anual de largo plazo del **Banco Mundial** (FP.CPI.TOTL.ZG). |
| **Desempleo** | Tasa trimestral nacional (GEIH) con anotación del pico de la pandemia y comparador entre ciudades principales. |
| **Exportaciones** | Composición de la canasta exportadora, top de productos por año y serie histórica del petróleo. |
| **Calculadoras** | Poder adquisitivo histórico, tu salario en dólares (frente al SMMLV 2026 de $1.750.905) y devaluación entre dos momentos. |

```bash
streamlit run app/main.py
```

## API REST

`FastAPI` con documentación interactiva en `/docs`. Sin autenticación — datos públicos. Respuestas reales:

| Endpoint | Devuelve | Ejemplo de respuesta |
|----------|----------|----------------------|
| `GET /trm` | TRM vigente COP/USD | `{"fecha":"vigente","trm_cop_usd":3588.09,"fuente":"datos.gov.co / Banco de la República"}` |
| `GET /ipc?anio=2023` | Inflación anual + serie mensual | `{"anio":2023,"variacion_promedio_anual_pct":11.58,"registros_mensuales":12}` |
| `GET /desempleo` | Tasa trimestral por ciudad/nacional | `{"ambito":"nacional","registros":40,"datos":[{"año":2015,"trimestre":1,"tasa_desempleo":10.8}]}` |
| `GET /smmlv?anio=2024` | Salario mínimo en COP y USD | `{"anio":2024,"smmlv_cop":1300000,"smmlv_usd":362.31,"incremento_vs_anio_anterior_pct":12.07}` |
| `GET /exportaciones/top?n=3` | Top productos exportados | `{"top_n":3,"productos":[{"producto":"Petroleo y derivados","promedio_millones_usd":12361.2}]}` |
| `GET /health` | Estado del servicio | `{"status":"ok","version":"1.0.0","fuentes":["DANE","Banco de la República","datos.gov.co"]}` |

```bash
uvicorn api.main:app --reload    # → http://localhost:8000/docs
curl http://localhost:8000/ipc?anio=2023
```

```json
{
  "anio": 2023,
  "variacion_promedio_anual_pct": 11.58,
  "registros_mensuales": 12,
  "datos_mensuales": [
    {"periodo": "2023-01", "mes": 1, "ipc": 330.67, "variacion_mensual": 0.97, "variacion_anual": 13.48}
  ],
  "fuente": "DANE — Índice de Precios al Consumidor"
}
```

## Datos que se actualizan solos

Tres GitHub Actions mantienen los CSV frescos sin intervención manual:

| Workflow | Qué actualiza | Frecuencia |
|----------|---------------|------------|
| [`actualizar_trm.yml`](.github/workflows/actualizar_trm.yml) | TRM oficial desde datos.gov.co. | Diaria |
| [`actualizar_ipc.yml`](.github/workflows/actualizar_ipc.yml) | Inflación anual del Banco Mundial (`scripts/actualizar_ipc_anual.py`). | Mensual |
| [`daily_update.yml`](.github/workflows/daily_update.yml) | Refresco general de series. | Diaria |

## Instalación

```bash
# 1. Clonar e instalar
git clone https://github.com/Brausin/colombia-data-insights.git
cd colombia-data-insights
pip install -e .

# 2. Dashboard interactivo (Streamlit)
streamlit run app/main.py

# 3. API REST (FastAPI + Uvicorn) → http://localhost:8000/docs
uvicorn api.main:app --reload

# 4. Pruebas
pytest -q          # 113 passing
```

## Fuentes de datos

| Indicador | Fuente | Frecuencia | Enlace oficial |
|-----------|--------|------------|----------------|
| TRM (COP/USD) | Superintendencia Financiera vía datos.gov.co | Diaria | [datos.gov.co](https://www.datos.gov.co/resource/32sa-8pi3.json) |
| Inflación (IPC) | DANE | Mensual | [dane.gov.co/ipc](https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-precios-al-consumidor-ipc) |
| Inflación anual | Banco Mundial (FP.CPI.TOTL.ZG) | Anual | [data.worldbank.org](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=CO) |
| Desempleo (GEIH) | DANE | Trimestral | [dane.gov.co/mercado-laboral](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral) |
| Exportaciones | DANE — Comercio Exterior | Anual | [dane.gov.co/exportaciones](https://www.dane.gov.co/index.php/estadisticas-por-tema/comercio-internacional/exportaciones) |
| Salario mínimo (SMMLV) | Ministerio de Trabajo | Anual | [mintrabajo.gov.co](https://www.mintrabajo.gov.co/) |

## Estructura

```
colombia-data-insights/
├── src/colombia_data/
│   ├── trm_live.py        # TRM en tiempo real
│   ├── trm.py             # histórico de tasa de cambio
│   ├── ipc.py             # inflación / IPC
│   ├── desempleo.py       # mercado laboral por ciudad
│   ├── exportaciones.py   # comercio exterior
│   ├── utils.py           # SMMLV y poder adquisitivo
│   └── fetcher.py         # descarga de fuentes oficiales
├── api/
│   └── main.py            # API REST (FastAPI)
├── app/
│   ├── main.py            # dashboard (Streamlit, 5 pestañas)
│   └── ui.py              # sistema de diseño data-dense BI
├── data/processed/        # CSVs limpios (IPC, inflación anual, desempleo…)
├── scripts/               # actualizadores (IPC anual del Banco Mundial)
├── notebooks/             # 6 notebooks de análisis
├── assets/visualizaciones/# PNGs generados
└── tests/                 # 113 pruebas (incluye smoke AppTest del dashboard)
```

## Stack

| Capa | Tecnología | Para qué |
|------|-----------|----------|
| Datos | **pandas / numpy** | limpieza y análisis de las series |
| Dashboard | **Streamlit + Plotly** | visualización interactiva con filtros y exportes |
| API | **FastAPI + Uvicorn** | endpoints REST públicos |
| Automatización | **GitHub Actions** | TRM diaria e IPC mensual sin intervención |
| Calidad | **pytest** | 113 pruebas automatizadas |
| Fuentes | **DANE · Banco de la República · Banco Mundial · datos.gov.co** | datos oficiales |

## Hermanos de familia

| Proyecto | Qué resuelve |
|----------|--------------|
| [factura-co](https://github.com/Brausin/factura-co) | Cuánto recibes realmente al cobrar en dólares: comisiones, retención, aportes y renta. |
| [propuesta-co](https://github.com/Brausin/propuesta-co) | Cotizar bien y entregar propuestas en PDF que se ven profesionales. |

---

MIT © 2024–2026 Brausin
