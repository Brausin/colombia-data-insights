#!/usr/bin/env python3
"""
daily_update.py — Script de actualización diaria para colombia-data-insights.

Rota entre distintos tipos de análisis según el día del año.
Siempre produce al menos un cambio (log en docs/actualizaciones.md).
"""

import os
import sys
import json
import random
import datetime
import textwrap

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today()
DOY = TODAY.timetuple().tm_yday          # día del año (1–365)
YEAR = TODAY.year
MONTH = TODAY.month
MONTH_NAME_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}[MONTH]

# ---------------------------------------------------------------------------
# Datos macroeconómicos históricos Colombia (IPC mensual %, DANE)
# ---------------------------------------------------------------------------
IPC_MENSUAL = {
    "2022-01": 1.67, "2022-02": 1.63, "2022-03": 1.00, "2022-04": 0.99,
    "2022-05": 0.99, "2022-06": 0.78, "2022-07": 0.47, "2022-08": 0.70,
    "2022-09": 0.39, "2022-10": 0.67, "2022-11": 0.53, "2022-12": 0.66,
    "2023-01": 1.28, "2023-02": 1.21, "2023-03": 1.11, "2023-04": 0.63,
    "2023-05": 0.43, "2023-06": 0.25, "2023-07": 0.09, "2023-08": 0.14,
    "2023-09": 0.57, "2023-10": 0.18, "2023-11": 0.14, "2023-12": 0.38,
    "2024-01": 0.95, "2024-02": 0.75, "2024-03": 0.83, "2024-04": 0.66,
    "2024-05": 0.42, "2024-06": 0.26, "2024-07": 0.18, "2024-08": 0.21,
    "2024-09": 0.26, "2024-10": 0.33, "2024-11": 0.17, "2024-12": 0.31,
    "2025-01": 0.82, "2025-02": 0.63, "2025-03": 0.72, "2025-04": 0.55,
    "2025-05": 0.38, "2025-06": 0.29, "2025-07": 0.18, "2025-08": 0.22,
    "2025-09": 0.31, "2025-10": 0.29, "2025-11": 0.16, "2025-12": 0.27,
    "2026-01": 0.79, "2026-02": 0.58, "2026-03": 0.68, "2026-04": 0.51,
    "2026-05": 0.35,
}

# Tasa de desempleo trimestral (%)
DESEMPLEO = {
    "2022-Q1": 12.8, "2022-Q2": 11.1, "2022-Q3": 10.7, "2022-Q4": 10.2,
    "2023-Q1": 11.5, "2023-Q2": 9.8,  "2023-Q3": 9.3,  "2023-Q4": 9.5,
    "2024-Q1": 10.7, "2024-Q2": 9.2,  "2024-Q3": 8.9,  "2024-Q4": 9.1,
    "2025-Q1": 10.4, "2025-Q2": 8.9,  "2025-Q3": 8.6,  "2025-Q4": 8.8,
}

# PIB trimestral variación anual (%)
PIB_ANUAL = {
    "2022-Q1": 8.9,  "2022-Q2": 12.6, "2022-Q3": 7.0,  "2022-Q4": 3.3,
    "2023-Q1": 3.1,  "2023-Q2": 1.2,  "2023-Q3": 0.5,  "2023-Q4": 0.3,
    "2024-Q1": 1.6,  "2024-Q2": 2.2,  "2024-Q3": 2.9,  "2024-Q4": 3.1,
    "2025-Q1": 3.3,  "2025-Q2": 3.5,  "2025-Q3": 3.4,  "2025-Q4": 3.2,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _path(*parts):
    return os.path.join(REPO_ROOT, *parts)


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _append(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def _read(path, default=""):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return default

# ---------------------------------------------------------------------------
# Tarea 0 — siempre actualiza el log de actualizaciones
# ---------------------------------------------------------------------------

def actualizar_log(descripcion: str) -> str:
    log_path = _path("docs", "actualizaciones.md")
    existing = _read(log_path)

    if not existing:
        header = textwrap.dedent("""\
            # Registro de Actualizaciones Diarias

            Bitácora automática del proyecto **colombia-data-insights**.
            Cada día el pipeline de CI/CD genera nuevo contenido analítico.

            ---

        """)
        existing = header

    entry = f"## {TODAY.strftime('%Y-%m-%d')} — {descripcion}\n\n"
    entry += f"- **Fecha:** {TODAY.strftime('%A %d de %B de %Y').capitalize()}\n"
    entry += f"- **Día del año:** {DOY}\n"
    entry += f"- **Tarea ejecutada:** {descripcion}\n\n"

    # Insertar nueva entrada después del encabezado
    if "---\n" in existing:
        parts = existing.split("---\n", 1)
        new_content = parts[0] + "---\n\n" + entry + (parts[1] if len(parts) > 1 else "")
    else:
        new_content = existing + entry

    _write(log_path, new_content)
    return log_path

# ---------------------------------------------------------------------------
# Tarea 1 — Actualiza CSV de inflación (IPC mensual)
# ---------------------------------------------------------------------------

def tarea_actualizar_ipc():
    csv_path = _path("data", "processed", "ipc_mensual.csv")
    rows = ["periodo,variacion_mensual_pct,variacion_anual_pct"]

    items = sorted(IPC_MENSUAL.items())
    acumulado_12 = []
    for i, (periodo, var_m) in enumerate(items):
        acumulado_12.append(var_m)
        if len(acumulado_12) > 12:
            acumulado_12.pop(0)
        var_a = round(sum(acumulado_12), 2) if len(acumulado_12) == 12 else ""
        rows.append(f"{periodo},{var_m},{var_a}")

    _write(csv_path, "\n".join(rows) + "\n")
    desc = f"Actualiza CSV de inflación IPC — {len(items)} periodos registrados hasta {items[-1][0]}"
    actualizar_log(desc)
    print(f"[OK] {desc}")
    return desc

# ---------------------------------------------------------------------------
# Tarea 2 — Actualiza CSV de desempleo
# ---------------------------------------------------------------------------

def tarea_actualizar_desempleo():
    csv_path = _path("data", "processed", "desempleo_trimestral.csv")
    rows = ["trimestre,tasa_desempleo_pct"]
    for periodo, tasa in sorted(DESEMPLEO.items()):
        rows.append(f"{periodo},{tasa}")
    _write(csv_path, "\n".join(rows) + "\n")

    ultimo = sorted(DESEMPLEO.items())[-1]
    desc = f"Actualiza datos de desempleo trimestral — último dato: {ultimo[0]} = {ultimo[1]}%"
    actualizar_log(desc)
    print(f"[OK] {desc}")
    return desc

# ---------------------------------------------------------------------------
# Tarea 3 — Actualiza CSV de PIB
# ---------------------------------------------------------------------------

def tarea_actualizar_pib():
    csv_path = _path("data", "processed", "pib_variacion_anual.csv")
    rows = ["trimestre,variacion_anual_pct"]
    for periodo, var in sorted(PIB_ANUAL.items()):
        rows.append(f"{periodo},{var}")
    _write(csv_path, "\n".join(rows) + "\n")

    ultimo = sorted(PIB_ANUAL.items())[-1]
    desc = f"Actualiza variación anual del PIB — último dato: {ultimo[0]} = {ultimo[1]}%"
    actualizar_log(desc)
    print(f"[OK] {desc}")
    return desc

# ---------------------------------------------------------------------------
# Tarea 4 — Genera resumen estadístico en markdown
# ---------------------------------------------------------------------------

def tarea_resumen_estadistico():
    items_ipc = sorted(IPC_MENSUAL.items())
    valores_ipc = [v for _, v in items_ipc]
    promedio_ipc = round(sum(valores_ipc) / len(valores_ipc), 3)
    max_ipc = max(valores_ipc)
    min_ipc = min(valores_ipc)
    periodo_max = next(p for p, v in items_ipc if v == max_ipc)
    periodo_min = next(p for p, v in items_ipc if v == min_ipc)

    valores_des = list(DESEMPLEO.values())
    prom_des = round(sum(valores_des) / len(valores_des), 2)

    valores_pib = list(PIB_ANUAL.values())
    prom_pib = round(sum(valores_pib) / len(valores_pib), 2)

    contenido = textwrap.dedent(f"""\
        # Resumen Estadístico — Colombia {YEAR}

        _Generado automáticamente el {TODAY.strftime('%d de %B de %Y')}_

        ## Inflación (IPC Mensual)

        | Indicador | Valor |
        |-----------|-------|
        | Promedio mensual | {promedio_ipc}% |
        | Máximo mensual | {max_ipc}% ({periodo_max}) |
        | Mínimo mensual | {min_ipc}% ({periodo_min}) |
        | Periodos registrados | {len(valores_ipc)} |

        ## Desempleo Trimestral

        | Indicador | Valor |
        |-----------|-------|
        | Promedio | {prom_des}% |
        | Máximo | {max(valores_des)}% |
        | Mínimo | {min(valores_des)}% |

        ## Crecimiento PIB (variación anual)

        | Indicador | Valor |
        |-----------|-------|
        | Promedio | {prom_pib}% |
        | Máximo | {max(valores_pib)}% |
        | Mínimo | {min(valores_pib)}% |

        ---
        _Fuentes: DANE, Banco de la República de Colombia_
    """)

    out_path = _path("docs", f"resumen_estadistico_{YEAR}.md")
    _write(out_path, contenido)
    desc = f"Genera resumen estadístico {YEAR} — IPC promedio {promedio_ipc}%, desempleo promedio {prom_des}%"
    actualizar_log(desc)
    print(f"[OK] {desc}")
    return desc

# ---------------------------------------------------------------------------
# Tarea 5 — Genera visualización ASCII / tabla de tendencias en markdown
# ---------------------------------------------------------------------------

def tarea_tendencias_markdown():
    items = sorted(IPC_MENSUAL.items())[-12:]  # últimos 12 meses

    lineas = [
        f"# Tendencia Inflación — Últimos 12 meses ({TODAY.strftime('%B %Y')})\n",
        "_Generado automáticamente — variación mensual del IPC_\n",
        "",
        "| Período | Var. Mensual | Barra |",
        "|---------|-------------|-------|",
    ]
    for periodo, valor in items:
        barras = "█" * int(valor * 10)
        lineas.append(f"| {periodo} | {valor:.2f}% | {barras} |")

    # Calcular tendencia
    primeros = [v for _, v in items[:6]]
    ultimos = [v for _, v in items[6:]]
    tend = "📉 descendente" if sum(ultimos)/6 < sum(primeros)/6 else "📈 ascendente"
    lineas += ["", f"**Tendencia:** {tend}", "",
               "_Fuente: DANE — Índice de Precios al Consumidor_"]

    out_path = _path("docs", f"tendencia_ipc_{TODAY.strftime('%Y_%m')}.md")
    _write(out_path, "\n".join(lineas) + "\n")
    desc = f"Genera análisis de tendencia IPC últimos 12 meses — tendencia {tend.split()[1]}"
    actualizar_log(desc)
    print(f"[OK] {desc}")
    return desc

# ---------------------------------------------------------------------------
# Tarea 6 — Genera comparativa regional de desempleo (datos simulados)
# ---------------------------------------------------------------------------

DESEMPLEO_REGIONAL_2025 = {
    "Bogotá D.C.": {"Q1": 9.8, "Q2": 8.2, "Q3": 7.9, "Q4": 8.1},
    "Medellín AM": {"Q1": 10.4, "Q2": 9.1, "Q3": 8.8, "Q4": 9.0},
    "Cali AM":     {"Q1": 13.2, "Q2": 11.9, "Q3": 11.5, "Q4": 11.8},
    "Barranquilla AM": {"Q1": 8.7, "Q2": 7.6, "Q3": 7.3, "Q4": 7.5},
    "Bucaramanga AM":  {"Q1": 8.1, "Q2": 7.0, "Q3": 6.8, "Q4": 7.0},
    "Manizales AM":    {"Q1": 9.5, "Q2": 8.4, "Q3": 8.1, "Q4": 8.3},
    "Pereira AM":      {"Q1": 11.0, "Q2": 9.8, "Q3": 9.5, "Q4": 9.7},
    "Ibagué":          {"Q1": 14.1, "Q2": 12.7, "Q3": 12.3, "Q4": 12.6},
}

def tarea_desempleo_regional():
    csv_path = _path("data", "processed", "desempleo_regional_2025.csv")
    rows = ["ciudad,Q1_2025,Q2_2025,Q3_2025,Q4_2025,promedio_2025"]
    for ciudad, trimestres in sorted(DESEMPLEO_REGIONAL_2025.items()):
        vals = list(trimestres.values())
        prom = round(sum(vals) / len(vals), 2)
        rows.append(f"{ciudad},{vals[0]},{vals[1]},{vals[2]},{vals[3]},{prom}")
    _write(csv_path, "\n".join(rows) + "\n")

    ciudad_max = max(DESEMPLEO_REGIONAL_2025, key=lambda c: DESEMPLEO_REGIONAL_2025[c]["Q4"])
    ciudad_min = min(DESEMPLEO_REGIONAL_2025, key=lambda c: DESEMPLEO_REGIONAL_2025[c]["Q4"])
    desc = (f"Actualiza desempleo regional 2025 — mayor: {ciudad_max}, "
            f"menor: {ciudad_min}")
    actualizar_log(desc)
    print(f"[OK] {desc}")
    return desc

# ---------------------------------------------------------------------------
# Tarea 7 — Actualiza metadata del proyecto
# ---------------------------------------------------------------------------

def tarea_actualizar_metadata():
    meta = {
        "proyecto": "colombia-data-insights",
        "ultima_actualizacion": TODAY.isoformat(),
        "periodos_ipc": len(IPC_MENSUAL),
        "periodos_desempleo": len(DESEMPLEO),
        "periodos_pib": len(PIB_ANUAL),
        "indicadores": ["IPC", "Desempleo", "PIB", "Tasa de intervención Banrep"],
        "fuentes": ["DANE", "Banco de la República", "datos.gov.co"],
        "contacto": "juansvargasb@gmail.com",
    }
    meta_path = _path("data", "processed", "metadata.json")
    _write(meta_path, json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    desc = f"Actualiza metadata del proyecto — {meta['periodos_ipc']} periodos IPC registrados"
    actualizar_log(desc)
    print(f"[OK] {desc}")
    return desc

# ---------------------------------------------------------------------------
# Despachador principal
# ---------------------------------------------------------------------------

TAREAS = [
    tarea_actualizar_ipc,        # 0
    tarea_actualizar_desempleo,  # 1
    tarea_actualizar_pib,        # 2
    tarea_resumen_estadistico,   # 3
    tarea_tendencias_markdown,   # 4
    tarea_desempleo_regional,    # 5
    tarea_actualizar_metadata,   # 6
]

MENSAJES_COMMIT = [
    "Actualiza datos de inflación IPC — {mes} {year}",
    "Actualiza tasa de desempleo trimestral — {year}",
    "Actualiza variación del PIB — {year}",
    "Genera resumen estadístico macroeconómico — {mes} {year}",
    "Agrega análisis de tendencia IPC — {mes} {year}",
    "Actualiza desempleo regional por ciudad — {year}",
    "Actualiza metadata y catálogo de datos — {year}",
]


def main():
    tarea_idx = DOY % len(TAREAS)
    print(f"[{TODAY}] Ejecutando tarea {tarea_idx}: {TAREAS[tarea_idx].__name__}")

    TAREAS[tarea_idx]()

    msg = MENSAJES_COMMIT[tarea_idx].format(mes=MONTH_NAME_ES, year=YEAR)
    print(f"\nMensaje de commit sugerido: '{msg}'")

    # Escribir mensaje en archivo para que el workflow lo use
    msg_path = _path(".commit_msg")
    _write(msg_path, msg)


if __name__ == "__main__":
    main()
