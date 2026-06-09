<div align="center">

# 🇨🇴 Colombia Data Insights

*Los datos económicos públicos de Colombia, por fin usables: dashboard, librería y API REST.*

![Tests](https://img.shields.io/badge/tests-109%20passing-brightgreen?style=flat-square&logo=pytest)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![API](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)
![Fuente](https://img.shields.io/badge/datos-Banco%20Rep%C3%BAblica%20%C2%B7%20DANE-yellow?style=flat-square)

</div>

---

## El problema

Colombia publica una montaña de datos económicos —inflación del DANE, TRM del Banco de la República, exportaciones, desempleo, salario mínimo— pero viven dispersos en PDFs, anexos de Excel y portales lentos. Para responder algo tan simple como *"¿cuánto se devaluó el peso este año?"* o *"¿la inflación de 2023 superó la meta del Banco de la República?"* toca descargar planillas y pelear con ellas. **Colombia Data Insights** toma esas fuentes oficiales y las entrega de tres formas listas para usar: un **dashboard** interactivo, una **librería** de Python y una **API REST** pública.

## Dashboard

Construido en Streamlit, con tema oscuro de BI y gráficas Plotly:

| Pestaña | Qué muestra |
|---------|-------------|
| 💵 **TRM** | Evolución histórica del dólar, devaluación anual y calculadora USD → COP en vivo. |
| 📈 **Inflación** | IPC anual vs. la meta del 3 % del Banco de la República, con lectura automática del año. |
| 👔 **Desempleo** | Tasa trimestral nacional y comparación entre las principales ciudades. |
| 🛢️ **Exportaciones** | Top de productos exportados y composición de la canasta exportadora. |
| 🧮 **Calculadoras** | Poder adquisitivo histórico y conversión de SMMLV a dólares. |

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

## Instalación

```bash
# 1. Clonar e instalar
git clone https://github.com/Brausin/colombia-data-insights.git
cd colombia-data-insights
pip install -e .
```

```bash
# 2. Dashboard interactivo (Streamlit)
streamlit run app/main.py
```

```bash
# 3. API REST (FastAPI + Uvicorn) → http://localhost:8000/docs
uvicorn api.main:app --reload
```

```bash
# 4. Pruebas
pytest -q          # 109 passing
```

## Fuentes de datos

| Indicador | Fuente | Frecuencia | Enlace oficial |
|-----------|--------|------------|----------------|
| TRM (COP/USD) | Superintendencia Financiera vía datos.gov.co | Diaria | [datos.gov.co](https://www.datos.gov.co/resource/32sa-8pi3.json) |
| Inflación (IPC) | DANE | Mensual | [dane.gov.co/ipc](https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-precios-al-consumidor-ipc) |
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
│   ├── main.py            # dashboard (Streamlit)
│   └── ui.py              # sistema de diseño BI oscuro
├── data/processed/        # CSVs limpios (IPC, desempleo, exportaciones…)
├── notebooks/             # 6 notebooks de análisis
├── assets/visualizaciones/# PNGs generados
└── tests/                 # 109 pruebas
```

## Stack

| Capa | Tecnología | Para qué |
|------|-----------|----------|
| Datos | **pandas / numpy** | limpieza y análisis de las series |
| Dashboard | **Streamlit + Plotly** | visualización interactiva |
| API | **FastAPI + Uvicorn** | endpoints REST públicos |
| Calidad | **pytest** | 109 pruebas automatizadas |
| Fuentes | **DANE · Banco de la República · datos.gov.co** | datos oficiales |

---

MIT © 2024 Brausin
