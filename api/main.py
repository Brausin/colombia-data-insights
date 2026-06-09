"""
colombia-data-insights — API REST
==================================
Endpoints públicos para consultar indicadores económicos colombianos.

Fuentes: DANE, Banco de la República, datos.gov.co
Documentación interactiva: /docs
Sin autenticación (datos de acceso público).

Uso::

    uvicorn api.main:app --reload
    # Luego: http://localhost:8000/docs
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from colombia_data.trm_live import get_trm_hoy, get_historico_trm
from colombia_data.ipc import get_ipc, variacion_ipc
from colombia_data.desempleo import get_desempleo, comparar_ciudades, CIUDADES_DISPONIBLES
from colombia_data.exportaciones import get_exportaciones, top_productos
from colombia_data.utils import smmlv_a_usd, calcular_poder_adquisitivo

app = FastAPI(
    title="Colombia Data Insights API",
    description=(
        "Indicadores económicos colombianos de fuentes oficiales. "
        "Datos del DANE, Banco de la República y Superintendencia Financiera. "
        "Sin autenticación requerida — datos de acceso público."
    ),
    version="1.0.0",
    contact={
        "name": "Colombia Data Insights",
        "url": "https://github.com/Brausin/colombia-data-insights",
    },
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

_log = logging.getLogger("colombia_data.api")

_FUENTE_NO_DISPONIBLE = (
    "Fuente de datos no disponible temporalmente. Intente de nuevo más tarde."
)


def _fuente_no_disponible(exc: Exception) -> HTTPException:
    """
    Convierte un fallo de carga de datos en un 503 limpio.

    El error real (que puede incluir rutas del servidor) se registra solo en
    los logs; al cliente se le devuelve un mensaje genérico que no expone la
    estructura interna del servidor.
    """
    _log.error("Fallo al cargar fuente de datos: %s", exc)
    return HTTPException(status_code=503, detail=_FUENTE_NO_DISPONIBLE)


def _col_anio(df) -> Optional[str]:
    """Localiza la columna de año del dataset (acepta 'anio', 'año' o 'year')."""
    return next(
        (c for c in df.columns if c.lower() in ("anio", "año", "year")),
        None,
    )


@app.get("/health", tags=["Sistema"])
def health_check():
    """Verifica que la API esté en línea."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "fuentes": ["DANE", "Banco de la República", "datos.gov.co"],
    }


@app.get("/trm", tags=["TRM"])
def obtener_trm(
    fecha: Optional[str] = Query(
        None,
        description="Fecha YYYY-MM-DD. Sin parámetro retorna TRM vigente.",
    )
):
    """
    Tasa Representativa del Mercado (COP/USD).

    Sin parámetros: TRM vigente. Con `fecha`: histórico más cercano.
    """
    try:
        trm = get_trm_hoy()
        historico = get_historico_trm(meses=60)

        if fecha:
            mes = fecha[:7]
            coincidencia = [h for h in historico if h["fecha"] == mes]
            if coincidencia:
                return {
                    "fecha": fecha,
                    "mes": mes,
                    "trm_cop_usd": coincidencia[0]["trm"],
                    "fuente": "Banco de la República",
                    "nota": "Promedio mensual",
                }
            raise HTTPException(
                status_code=404,
                detail=f"Sin datos de TRM para {mes}.",
            )

        return {
            "fecha": "vigente",
            "trm_cop_usd": trm,
            "fuente": "datos.gov.co / Banco de la República",
            "nota": "TRM vigente. Días no hábiles usan el último valor disponible.",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _fuente_no_disponible(exc) from exc


@app.get("/trm/historico", tags=["TRM"])
def historico_trm(
    meses: int = Query(12, ge=1, le=60, description="Meses a retornar (1-60)")
):
    """Histórico mensual de TRM para los últimos N meses."""
    try:
        datos = get_historico_trm(meses=meses)
        return {
            "meses": meses,
            "registros": len(datos),
            "datos": datos,
            "fuente": "Banco de la República de Colombia",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _fuente_no_disponible(exc) from exc


@app.get("/ipc", tags=["Inflación"])
def obtener_ipc(
    anio: Optional[int] = Query(None, description="Año (2015-2024). Sin parámetro retorna todos.")
):
    """
    Variación anual del IPC (inflación).

    Fuente: DANE — Índice de Precios al Consumidor.
    """
    try:
        df = get_ipc()
        col = _col_anio(df)
        if col is None:
            raise _fuente_no_disponible(
                ValueError("Dataset de IPC sin columna de año reconocible.")
            )

        if anio:
            df_anio = df[df[col] == anio]
            if df_anio.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"Sin datos de IPC para {anio}.",
                )
            cols_mensuales = [
                c
                for c in ("periodo", "mes", "ipc", "variacion_mensual", "variacion_anual")
                if c in df_anio.columns
            ]
            return {
                "anio": anio,
                "variacion_promedio_anual_pct": round(variacion_ipc(anio, anio), 2),
                "registros_mensuales": len(df_anio),
                "datos_mensuales": df_anio[cols_mensuales].to_dict(orient="records"),
                "fuente": "DANE — Índice de Precios al Consumidor",
            }

        anios = sorted(int(a) for a in df[col].unique())
        resumen = [
            {"anio": a, "variacion_promedio_pct": round(variacion_ipc(a, a), 2)}
            for a in anios
        ]
        return {
            "anios_disponibles": anios,
            "resumen_anual": resumen,
            "fuente": "DANE — Índice de Precios al Consumidor",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _fuente_no_disponible(exc) from exc


@app.get("/desempleo", tags=["Mercado laboral"])
def obtener_desempleo(
    ciudad: Optional[str] = Query(
        None,
        description="Ciudad (bogota, medellin, cali, barranquilla, bucaramanga, "
                    "manizales, ibague, pereira, cucuta, cartagena). Sin acento.",
    ),
    anio_inicio: int = Query(2015, description="Año de inicio del período"),
    anio_fin: int = Query(2024, description="Año de fin del período"),
):
    """
    Tasa de desempleo trimestral por período.

    Sin parámetros: serie nacional 2015-2024.
    Con `ciudad`: serie de esa ciudad específica.

    Fuente: DANE — Gran Encuesta Integrada de Hogares (GEIH).

    Ciudades disponibles: bogota, medellin, cali, barranquilla, bucaramanga,
    manizales, ibague, pereira, cucuta, cartagena.
    """
    try:
        try:
            df = get_desempleo(anio_inicio=anio_inicio, anio_fin=anio_fin, ciudad=ciudad)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc) + f". Ciudades disponibles: {', '.join(CIUDADES_DISPONIBLES)}",
            )

        datos = df.to_dict(orient="records")

        return {
            "ambito": ciudad if ciudad else "nacional",
            "anio_inicio": anio_inicio,
            "anio_fin": anio_fin,
            "registros": len(datos),
            "datos": datos,
            "fuente": "DANE — Gran Encuesta Integrada de Hogares",
            "ciudades_disponibles": CIUDADES_DISPONIBLES,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _fuente_no_disponible(exc) from exc


@app.get("/smmlv", tags=["Salario"])
def obtener_smmlv(
    anio: int = Query(2024, description="Año de consulta (2018-2026)")
):
    """
    Salario Mínimo Mensual Legal Vigente (SMMLV) en COP y USD.

    Fuente: Ministerio de Trabajo — Decretos anuales de SMMLV.
    """
    smmlv_por_anio = {
        2018: 781_242, 2019: 828_116, 2020: 877_803, 2021: 908_526,
        2022: 1_000_000, 2023: 1_160_000, 2024: 1_300_000,
        2025: 1_423_500, 2026: 1_550_000,
    }
    if anio not in smmlv_por_anio:
        raise HTTPException(
            status_code=404,
            detail=f"Sin datos para {anio}. Disponibles: {sorted(smmlv_por_anio.keys())}",
        )
    try:
        smmlv_cop = smmlv_por_anio[anio]
        trm = get_trm_hoy()
        anio_ant = anio - 1
        incremento = (
            round((smmlv_cop / smmlv_por_anio[anio_ant] - 1) * 100, 2)
            if anio_ant in smmlv_por_anio else None
        )
        return {
            "anio": anio,
            "smmlv_cop": smmlv_cop,
            "smmlv_usd": round(smmlv_cop / trm, 2),
            "trm_usada": trm,
            "incremento_vs_anio_anterior_pct": incremento,
            "fuente": "Ministerio de Trabajo de Colombia",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _fuente_no_disponible(exc) from exc


@app.get("/exportaciones", tags=["Comercio exterior"])
def obtener_exportaciones(
    producto: Optional[str] = Query(None, description="Filtrar por producto (petroleo, cafe, carbon)"),
    desde: Optional[int] = Query(None, description="Año inicio"),
    hasta: Optional[int] = Query(None, description="Año fin"),
):
    """
    Exportaciones colombianas por producto. Valores en millones USD FOB.

    Fuente: DANE — Estadísticas de Comercio Exterior.
    """
    try:
        df = get_exportaciones(anio_inicio=desde or 2010, anio_fin=hasta or 2024)
        if producto:
            termino = producto.lower().replace("é", "e").replace("ó", "o")
            mask = df["producto"].str.lower().str.contains(termino, na=False)
            df = df[mask]
            if df.empty:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "mensaje": f"No encontrado: '{producto}'",
                        "disponibles": get_exportaciones()["producto"].unique().tolist(),
                    },
                )
        return {
            "registros": len(df),
            "datos": df.to_dict(orient="records"),
            "fuente": "DANE — Estadísticas de Comercio Exterior",
            "unidad": "Millones USD FOB",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _fuente_no_disponible(exc) from exc


@app.get("/exportaciones/top", tags=["Comercio exterior"])
def top_exportaciones(
    n: int = Query(5, ge=1, le=20, description="N principales productos"),
    anio: Optional[int] = Query(None, description="Año de consulta"),
):
    """Top N productos de exportación por año."""
    try:
        top = top_productos(anio=anio, n=n)
        return {
            "anio": anio or "promedio histórico",
            "top_n": n,
            "productos": top.to_dict(orient="records"),
            "fuente": "DANE — Estadísticas de Comercio Exterior",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _fuente_no_disponible(exc) from exc
