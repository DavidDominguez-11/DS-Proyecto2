# Proyecto 2 — Predicción de Compradores Recurrentes

**CC3084 – Data Science | Universidad del Valle de Guatemala | Semestre II – 2026**

## Descripción

Este repositorio contiene el **Proyecto 2** del curso CC3084 – Data Science, correspondiente al **Reto #11: "Predicción de compradores recurrentes: cuestionar la línea base"** (tema: Negocios).

El proyecto tiene dos fases:

1. **Análisis exploratorio (EDA)** de los registros de actividad, perfiles de usuario y etiquetas de recompra de la plataforma Tmall (Alibaba), para identificar patrones asociados con que un usuario vuelva a comprar a un mismo vendedor.
2. **Resultados**: ingeniería de variables, entrenamiento y comparación de modelos de clasificación (Regresión Logística, Random Forest, LightGBM y un ensamble) que estiman la probabilidad de recompra, y una aplicación interactiva para explorar los datos y clasificar nuevos pares usuario-vendedor.

## Enlace al Reto Original

- [Predicción de compradores recurrentes — Tianchi (Alibaba)](https://tianchi.aliyun.com/competition/entrance/231576/information)

## Estructura del Repositorio

```
DS-Proyecto2/
├── README.md                              # Este archivo
├── .gitignore                             # Archivos excluidos de Git
├── data/                                  # Datos locales (NO incluidos en Git)
│   ├── data_format1/
│   │   ├── train_format1.csv              # Pares usuario-vendedor con etiqueta
│   │   ├── test_format1.csv               # Pares usuario-vendedor a predecir
│   │   ├── user_info_format1.csv          # Información demográfica de usuarios
│   │   └── user_log_format1.csv           # Registro de actividad (~1.9 GB)
│   ├── sample_submission.csv              # Formato de envío de predicciones
│   └── processed/                         # Generado por el notebook 02 (parquet)
├── docs/
│   ├── Proyecto2EDA.md                    # Guía de la fase de EDA
│   ├── Proyecto2Resultados.md             # Guía de la fase de resultados
│   ├── 01_…05_*.md                        # Documentación de la fase de EDA
│   └── 06_…11_*.md                        # Documentación de la fase de resultados
├── notebooks/
│   ├── proyecto2_eda.ipynb                # 1. Análisis exploratorio
│   ├── 02_ingenieria_variables.ipynb      # 2. Variables de modelado y partición
│   └── 03_modelado.ipynb                  # 3. Ajuste, evaluación y comparación de modelos
├── outputs/
│   ├── figures/                           # Figuras 01–24; app/ contiene capturas de la aplicación
│   ├── tables/                            # Tablas exportadas por los notebooks
│   └── models/                            # Modelos entrenados y artefactos para la aplicación
├── app/                                   # Aplicación Streamlit (app.py, paginas/, data/)
├── .streamlit/config.toml                 # Tema de colores de la aplicación
└── requirements.txt                       # Dependencias (Python 3.12)
```

## Datos

Los datos **no están incluidos en el repositorio** (están en `.gitignore`) debido a su tamaño. Para ejecutar el notebook, los archivos deben colocarse localmente en la estructura indicada:

```
data/
├── data_format1/
│   ├── train_format1.csv
│   ├── test_format1.csv
│   ├── user_info_format1.csv
│   └── user_log_format1.csv
└── sample_submission.csv
```

Para obtener los datos, leer `data.md`.

> **Importante**: El archivo `user_log_format1.csv` ocupa aproximadamente 1.9 GB. El notebook de EDA lo procesa por fragmentos (`chunksize`); el notebook 02 lo carga completo con tipos compactos (~1 GB en memoria) y lo guarda en parquet (`data/processed/`).

## Cómo Ejecutar los Notebooks

### Prerrequisitos

- Python 3.12 (recomendado; es la versión usada para ejecutar el proyecto)
- Al menos 8 GB de RAM libres (el notebook 02 carga el registro de actividad completo, ~1 GB con tipos compactos, y genera copias intermedias)

### Entorno virtual

Desde la **raíz del repositorio**:

```bash
# Windows
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m ipykernel install --sys-prefix --name proyecto2 --display-name "Python (proyecto2 .venv)"

# Linux / macOS
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --sys-prefix --name proyecto2 --display-name "Python (proyecto2 .venv)"
```

La carpeta `.venv/` está excluida de Git.

### Ejecución

1. Clonar el repositorio.
2. Colocar los datos en la estructura `data/` descrita arriba.
3. Crear el entorno virtual (sección anterior).
4. Abrir el notebook con el kernel **Python (proyecto2 .venv)**:

```bash
.venv/Scripts/python -m jupyter notebook notebooks/proyecto2_eda.ipynb
```

O ejecutarlo completo desde la terminal (usar `python -m nbconvert` del entorno virtual, no el comando global `jupyter`):

```bash
.venv/Scripts/python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 --ExecutePreprocessor.kernel_name=proyecto2 notebooks/proyecto2_eda.ipynb
```

Los notebooks se ejecutan en orden:

| Notebook | Contenido | Genera |
|---|---|---|
| `notebooks/proyecto2_eda.ipynb` | Análisis exploratorio | `outputs/figures/01`–`16`, tablas del EDA |
| `notebooks/02_ingenieria_variables.ipynb` | Variables de modelado y partición | `data/processed/*.parquet`, figura `17`, diccionario de variables |
| `notebooks/03_modelado.ipynb` | Ajuste, evaluación y comparación de modelos (~45 min) | `outputs/models/`, figuras `18`–`24`, tablas de resultados |

> **Nota**: La ejecución completa puede tomar varios minutos debido al procesamiento del archivo de logs (~55 millones de registros). Las figuras se guardan en `outputs/figures/` y las tablas en `outputs/tables/`.

## Aplicación

Aplicación web (Streamlit) para explorar los datos, comparar los modelos y clasificar nuevos pares usuario-vendedor. Usa los datos compactos de `app/data/` y los modelos de `outputs/models/`, así que **no necesita** el registro de actividad de 1.9 GB.

```bash
# Desde la raíz del repositorio, con el entorno virtual creado
.venv/Scripts/python -m streamlit run app/app.py
```

Si se vuelven a ejecutar los notebooks 02 o 03, regenerar los datos de la aplicación con `.venv/Scripts/python app/preparar_datos.py`. Detalles en [`docs/10_aplicacion.md`](docs/10_aplicacion.md).

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [`01_contexto_investigacion.md`](docs/01_contexto_investigacion.md) | Situación problemática, problema científico, objetivos e investigación del tema. |
| [`02_descripcion_datos.md`](docs/02_descripcion_datos.md) | Descripción detallada de cada archivo, diccionario de datos y relaciones. |
| [`03_limpieza_preprocesamiento.md`](docs/03_limpieza_preprocesamiento.md) | Revisiones de calidad, decisiones de limpieza y variables derivadas. |
| [`04_hallazgos_conclusiones.md`](docs/04_hallazgos_conclusiones.md) | Hallazgos principales, implicaciones para el modelado, limitaciones y siguientes pasos. |
| [`05_resultados_interpretacion.md`](docs/05_resultados_interpretacion.md) | Resultados detallados del EDA (incluye análisis temporal, Spearman y pruebas estadísticas). |
| [`06_revision_bibliografica.md`](docs/06_revision_bibliografica.md) | Revisión bibliográfica, selección de algoritmos y métricas (fase de resultados). |
| [`07_metodologia_modelado.md`](docs/07_metodologia_modelado.md) | Metodología de modelado: partición, variables, ajuste, evaluación y herramientas. |
| [`08_ingenieria_variables.md`](docs/08_ingenieria_variables.md) | Ingeniería de variables (64), partición entrenamiento/prueba y poder predictivo individual. |
| [`09_modelado_resultados.md`](docs/09_modelado_resultados.md) | Ajuste de hiperparámetros, evaluación en prueba, comparación y selección de modelos. |
| [`10_aplicacion.md`](docs/10_aplicacion.md) | Aplicación Streamlit: tecnologías, páginas, preprocesamiento transparente, teoría del color y pruebas. |
| [`11_conclusiones.md`](docs/11_conclusiones.md) | Cumplimiento de objetivos, efectividad de los algoritmos, recomendaciones, limitaciones y trabajo futuro. |
