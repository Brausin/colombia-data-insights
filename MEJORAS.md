# Mejoras — colombia-data-insights

## Archivos MODIFICADOS (reemplazar los existentes)
| Archivo | Cambio |
|---|---|
| `src/colombia_data/ipc.py` | **Bug de rendimiento**: `_cargar_ipc()` leía el CSV completo HASTA 3 VECES por llamada (la expresión `pd.read_csv(ruta, nrows=0)` estaba anidada dentro del `parse_dates` de otro `read_csv`). Ahora lee el encabezado una vez y el archivo una sola vez. Como `get_ipc()` se llama en cada request de la API y cada carga del dashboard, esto reduce el I/O del endpoint `/ipc` a un tercio. También se eliminó el import `os` sin usar. Comportamiento idéntico: tus 109 tests no se afectan. |
| `setup.py` | Versión `0.1.0 → 0.2.0` para coincidir con `__version__ = "0.2.0"` de `__init__.py` (estaban desincronizadas). `open()` del README ahora con `encoding="utf-8"` (en Windows fallaba con caracteres como 🇨🇴 del README). |

## Archivos NUEVOS
| Archivo | Qué hace |
|---|---|
| `.github/dependabot.yml` | Actualizaciones automáticas mensuales de dependencias. |

## Detectado pero NO tocado (decide tú)
- `src/colombia_data/trm.py` importa `os` sin usarlo (limpieza menor, no incluí el archivo completo solo por eso).
- `fetcher.py` (`BancoRepublicaClient.obtener_ipc`) retorna datos embebidos en el código, no consulta la API real del Banco de la República. Funciona como snapshot offline, pero el nombre "Client" sugiere otra cosa; vale la pena documentarlo en el docstring.
- El diccionario `_TRM_RESPALDO` de `trm_live.py` llega hasta 2026-06; recuerda extenderlo periódicamente (o automatizarlo con el cron que ya mencionas en el dashboard).

## Verificación realizada
- `ipc.py` probado con dataset sintético de la misma estructura: `get_ipc`, `variacion_ipc` y `ajustar_por_inflacion` devuelven los mismos resultados que la versión original (lógica intacta), con 1 lectura de archivo en lugar de 3. ✔

---

# Mejoras de UI (rediseño con la skill ui-ux-pro-max)

Design system generado con la skill: **"Data-Dense Dashboard"**, tema oscuro
profesional — documentado en `design-system/colombia-data-insights/MASTER.md`.
Solo cambió la capa de presentación; la lógica de `src/` quedó intacta y las
firmas que consume la UI son las mismas.

## Archivos MODIFICADOS
| Archivo | Cambio |
|---|---|
| `app/ui.py` | Design system nuevo: fondo `#020617` con paneles `#0F172A`, acentos de dato (verde positivo, rojo negativo, cian/ámbar para series) y el amarillo bandera reservado como acento de marca. Tipografía **Fira Sans + Fira Code** (cifras tabulares). Componentes nuevos: `callout()` (avisos con icono SVG que reemplazan a `st.info/warning/success` con emoji), `empty_state()` (estados vacíos explícitos), `header_app()` (wordmark con hairline tricolor en vez del emoji 🇨🇴), `fuente_dato()` (pie de fuente por gráfico) e iconos SVG estilo Lucide. CSS: foco visible en todos los controles, hover sin saltos de layout (150–250 ms), `prefers-reduced-motion`, scrollbar y multiselect tematizados, responsive <740 px. Template Plotly con colorway distinguible y ejes en Fira Code. |
| `app/main.py` | **Sin emojis como iconos**: tabs con Material Symbols (`:material/...:`), avisos con `callout()`. **Bugs corregidos**: (1) año de IPC sin filas válidas ya no crashea (`idxmax` sobre vacío) → estado vacío; (2) si falta `data/processed/inflacion_anual.csv` la app ya no muere con `FileNotFoundError` → estado vacío con instrucciones; (3) defaults de TRM acotados con `_clamp()` — antes, una TRM en vivo fuera del rango del `number_input` rompía la página (StreamlitAPIException); (4) `comparar_ciudades` con manejo de errores específico (año sin datos) y estado vacío si el resultado no tiene filas; (5) exportaciones: guardas para CSV vacío y año sin registros; (6) carga inicial envuelta en try → pantalla de error en español con botón «Reintentar» (limpia caché); (7) etiquetas de barras con `cliponaxis=False` para que no se corten. |

## Archivos NUEVOS
| Archivo | Qué hace |
|---|---|
| `.streamlit/config.toml` | Tema base oscuro para que los widgets nativos (slider, selectbox, date picker, alertas) no rendericen en claro rompiendo el diseño. |
| `design-system/colombia-data-insights/MASTER.md` | Design system completo generado por la skill (paleta, tipografía, espaciado, componentes, anti-patrones, checklist). |

## Verificación de UI realizada
- 9 escenarios sobre un doble de pruebas estricto de Streamlit (valida rangos
  de widgets, mezcla int/float, `format_func` sobre todas las opciones,
  pertenencia de valores) + pandas real: todas las tabs, año IPC parcial,
  0/1 ciudades, conversor en 0, CSV anual ausente y TRM extrema (900 y 25.000). ✔
- Checklist de la skill: sin emojis como iconos ✔ · contraste verificado
  programáticamente (texto 19.3:1, muted 7.9:1, todos ≥4.5:1) ✔ · focus
  visible ✔ · `prefers-reduced-motion` ✔ · hover sin layout shift ✔.
- Nota: el sandbox no permite instalar Streamlit real (sin red a PyPI);
  recomendado un `streamlit run app/main.py` local como humo final.
