# Proyecto 2 — Análisis Exploratorio de Datos

**CC3084 – Data Science | Universidad del Valle de Guatemala | Semestre II – 2026**

## Descripción

Este repositorio contiene el **Proyecto 2** del curso CC3084 – Data Science, correspondiente al **Reto #11: "Predicción de compradores recurrentes: cuestionar la línea base"** (tema: Negocios).

El objetivo del proyecto es realizar un **análisis exploratorio de datos (EDA)** completo sobre los registros de actividad, perfiles de usuario y etiquetas de recompra de la plataforma Tmall (Alibaba), para identificar patrones de comportamiento y características demográficas asociadas con que un usuario vuelva a comprar a un mismo vendedor.

> **Alcance**: Este proyecto se centra exclusivamente en el análisis exploratorio de datos. **No se entrenan modelos predictivos** ni se genera un archivo de predicción.

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
│   └── sample_submission.csv              # Formato de envío de predicciones
├── docs/
│   ├── Proyecto2EDA.md                    # Guía obligatoria del proyecto
│   ├── 01_contexto_investigacion.md       # Contexto, problema y objetivos
│   ├── 02_descripcion_datos.md            # Descripción detallada de los datos
│   ├── 03_limpieza_preprocesamiento.md    # Limpieza y decisiones de calidad
│   ├── 04_hallazgos_conclusiones.md       # Hallazgos, limitaciones y pasos futuros
│   └── 05_resultados_interpretacion.md    # Resultados detallados e interpretación numérica
├── notebooks/
│   └── proyecto2_eda.ipynb                # Notebook principal con todo el EDA
└── outputs/
    ├── figures/                           # Figuras generadas por el notebook
    └── tables/                            # Tablas exportadas por el notebook
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

> **Importante**: El archivo `user_log_format1.csv` ocupa aproximadamente 1.9 GB. El notebook utiliza lectura por fragmentos (`chunksize`) para procesarlo de forma eficiente.

## Cómo Ejecutar el Notebook

### Prerrequisitos

- Python 3.8 o superior
- Paquetes requeridos: `pandas`, `numpy`, `matplotlib`, `seaborn`

Instalación de dependencias:
```bash
pip install -r requirements.txt
```
o  
```bash
pip install pandas numpy matplotlib seaborn
```

### Ejecución

1. Clonar el repositorio.
2. Colocar los datos en la estructura `data/` descrita arriba.
3. Ejecutar el notebook desde la **raíz del repositorio**:

```bash
jupyter notebook notebooks/proyecto2_eda.ipynb
```

O alternativamente:
```bash
jupyter nbconvert --to notebook --execute notebooks/proyecto2_eda.ipynb --output proyecto2_eda_ejecutado.ipynb
```

> **Nota**: La ejecución completa puede tomar varios minutos debido al procesamiento del archivo de logs (~55 millones de registros).

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [`01_contexto_investigacion.md`](docs/01_contexto_investigacion.md) | Situación problemática, problema científico, objetivos e investigación del tema. |
| [`02_descripcion_datos.md`](docs/02_descripcion_datos.md) | Descripción detallada de cada archivo, diccionario de datos y relaciones. |
| [`03_limpieza_preprocesamiento.md`](docs/03_limpieza_preprocesamiento.md) | Revisiones de calidad, decisiones de limpieza y variables derivadas. |
| [`04_hallazgos_conclusiones.md`](docs/04_hallazgos_conclusiones.md) | Hallazgos principales, limitaciones y siguientes pasos. |
| [`05_resultados_interpretacion.md`](docs/05_resultados_interpretacion.md) | Resultados detallados, cifras, tablas y figuras interpretadas. |
