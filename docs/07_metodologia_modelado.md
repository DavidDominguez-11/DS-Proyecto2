# Metodología de Modelado

Este documento describe la metodología definida para la fase de modelado del proyecto (guía *Proyecto 2 — Resultados*): objetivos de la fase, partición de los datos, ingeniería de variables, entrenamiento, ajuste de hiperparámetros, evaluación, herramientas y aplicación.

> **Estado**: plan metodológico definido antes de la implementación. Los resultados de cada etapa se documentan en `08_ingenieria_variables.md`, `09_modelado_resultados.md`, `10_aplicacion.md` y `11_conclusiones.md`.

---

## 1. Objetivos de la fase de modelado

### 1.1 Objetivo general

Desarrollar, ajustar y comparar modelos de clasificación supervisada que estimen la probabilidad de que un comprador nuevo adquirido durante el Double 11 vuelva a comprar al mismo vendedor, e integrarlos en una aplicación interactiva que permita explorar los datos, consultar predicciones y comparar el rendimiento de los modelos.

### 1.2 Objetivos específicos

1. **Construir un conjunto de variables predictivas** a nivel de usuario, vendedor, par usuario-vendedor y temporal a partir de los registros de actividad, sin fuga de información de la variable objetivo.
2. **Entrenar y ajustar al menos tres algoritmos** (Regresión Logística, Random Forest y LightGBM) mediante validación cruzada estratificada y agrupada por usuario.
3. **Evaluar los modelos en un conjunto de prueba reservado** con AUC-ROC como métrica principal y AUC-PR, precisión, recall, F1 y tiempos de cómputo como métricas complementarias, y **seleccionar el mejor modelo**. Meta: superar a la Regresión Logística base y alcanzar un AUC-ROC ≥ 0.65 en prueba (referencia: la solución ganadora de la competencia reportó un AUC cercano a 0.70).
4. **Desarrollar una aplicación interactiva** que permita explorar las variables limpias, clasificar pares usuario-vendedor nuevos con uno o todos los modelos y visualizar (u ocultar) gráficas interactivas del rendimiento de cada modelo.

---

## 2. Pasos seguidos

1. Revisión bibliográfica y selección de algoritmos (`06_revision_bibliografica.md`).
2. Revisión y ampliación del análisis exploratorio: análisis temporal, correlación de Spearman y pruebas estadísticas (`02` a `05`).
3. Ingeniería de variables a partir de `user_log_format1.csv` y construcción de la tabla de modelado (`08_ingenieria_variables.md`).
4. Partición entrenamiento/prueba (`08_ingenieria_variables.md`).
5. Entrenamiento de modelos base y ajuste de hiperparámetros con validación cruzada (`09_modelado_resultados.md`).
6. Selección del umbral de decisión (`09_modelado_resultados.md`).
7. Evaluación final en el conjunto de prueba y comparación de modelos (`09_modelado_resultados.md`).
8. Exportación de modelos y artefactos para la aplicación (`09_modelado_resultados.md`).
9. Desarrollo de la aplicación (`10_aplicacion.md`).
10. Conclusiones (`11_conclusiones.md`).

---

## 3. Selección de los conjuntos de entrenamiento y prueba

### 3.1 Por qué no se usa `test_format1.csv` para evaluar

`test_format1.csv` es el conjunto de prueba de la competencia y **no contiene etiquetas** (columna `prob` vacía). Como la competencia está cerrada, no es posible obtener la evaluación oficial. Por ello, **toda la evaluación se hace sobre `train_format1.csv`** (260,864 pares etiquetados), dividiéndolo en entrenamiento y prueba.

### 3.2 Estructura de la partición original de la competencia

Al analizar los archivos originales se encontró que:

| Característica | Valor |
|---|---|
| Usuarios compartidos entre train y test oficiales | **0** |
| Vendedores compartidos entre train y test oficiales | **1,992 de 1,993** |
| Pares por usuario en train (media / máximo) | 1.23 / 18 |
| Pares por vendedor en train (mediana / máximo) | 52 / 3,379 |
| Tasa de recompra por vendedor (mín. / mediana / máx.) | 0.0 % / 4.3 % / 52.9 % |

Es decir, la competencia evalúa la capacidad de predecir para **usuarios nuevos con vendedores conocidos**.

### 3.3 Partición adoptada

- **Prueba (*hold-out*)**: 20 % de los pares, separados con `StratifiedGroupKFold` agrupando por `user_id` y estratificando por `label` (`random_state = 42`).
  - *Agrupada por usuario*: ningún usuario aparece en entrenamiento y prueba a la vez, reproduciendo la estructura oficial y evitando que el modelo "memorice" usuarios.
  - *Estratificada*: ambas particiones conservan ~6.1 % de clase positiva.
- **Entrenamiento**: 80 % restante. Sobre él se hace validación cruzada de 5 pliegues, también `StratifiedGroupKFold` por `user_id`, para ajustar hiperparámetros y elegir el umbral.
- **El conjunto de prueba se usa una sola vez**, al final, para reportar el rendimiento de los modelos ya ajustados.

| Conjunto | Pares | % | Usuarios | Vendedores | Positivos | Tasa de positivos |
|---|---:|---:|---:|---:|---:|---:|
| Entrenamiento | 208,691 | 80.0 % | 169,616 | 1,991 | 12,762 | 6.12 % |
| Prueba | 52,173 | 20.0 % | 42,446 | 1,988 | 3,190 | 6.11 % |

Cada pliegue de validación cruzada tiene ~41,738 pares (16 %) con 6.11–6.12 % de positivos. No hay usuarios compartidos entre entrenamiento y prueba ni entre pliegues, y 1,986 de los 1,988 vendedores de prueba aparecen en entrenamiento. Detalle en `08_ingenieria_variables.md`.

---

## 4. Ingeniería de variables

La revisión bibliográfica (Liu et al., 2016) y el EDA indican que la información útil está en varios niveles. Se construyeron **64 variables** (24 del par, 19 del usuario, 16 del vendedor, 3 de relación y 2 demográficas); la lista final y su poder predictivo individual están en `08_ingenieria_variables.md` y `outputs/tables/diccionario_variables.csv`. Plan original:

| Nivel | Variables previstas | Origen |
|---|---|---|
| **Par usuario-vendedor** | Las 13 del EDA (`clicks`, `cart`, `purchase`, `favorite`, `total_actions`, `n_items`, `n_cats`, `n_brands`, `n_days` y 4 tasas); actividad y compras en el Double 11 (11/11); actividad antes del Double 11; días con compra; primer/último día de interacción y duración de la relación | `user_log` |
| **Usuario** | Actividad total en la plataforma, número de vendedores con los que interactúa, compras totales, vendedores a los que compró en el Double 11, proporción de su actividad concentrada en el vendedor | `user_log` |
| **Vendedor** | Número de usuarios y compradores, conversión (compras / clics), número de productos, tasa histórica de recompra del vendedor (*target encoding*) | `user_log` y `train` |
| **Demográficas** | `age_range` (con `50+` consolidado) y `gender`, como categóricas | `user_info` |

### 4.1 Control de fuga de información

- Las variables provenientes de `user_log` no usan la etiqueta.
- La **tasa de recompra del vendedor** se calcula a partir de `label`, por lo que:
  - En entrenamiento se calcula *fuera de pliegue* (*out-of-fold*): cada observación recibe la tasa calculada sin su propio pliegue.
  - Para prueba y para la aplicación se usa la tasa calculada solo con el conjunto de entrenamiento.
  - Se suaviza hacia la tasa global (media bayesiana) para vendedores con pocos pares.
- Los parámetros de preprocesamiento (escalado, codificación) se ajustan solo con el conjunto de entrenamiento, dentro de un `Pipeline` de scikit-learn.

---

## 5. Preprocesamiento por modelo

| Paso | Regresión Logística | Random Forest | LightGBM |
|---|---|---|---|
| Transformación `log1p` de conteos | Sí (reduce el sesgo documentado en el EDA) | No necesario | No necesario |
| Estandarización | Sí | No | No |
| Codificación de edad y género | *One-hot* | Ordinal | Ordinal |
| Tratamiento de outliers | Atenuados por `log1p`; no se eliminan | Se conservan (árboles robustos) | Se conservan |
| Desbalance | `class_weight='balanced'` | `class_weight='balanced_subsample'` | `scale_pos_weight` (hiperparámetro; el mejor valor fue 1) |
| Tasa de recompra del vendedor | `TargetEncoder` (ajuste cruzado) + estandarización | `TargetEncoder` (ajuste cruzado) | `TargetEncoder` (ajuste cruzado) |

Los outliers se conservan, coherente con la decisión del EDA: representan comportamiento real de alta intensidad.

---

## 6. Ajuste de hiperparámetros

- **Método**: búsqueda aleatoria (`RandomizedSearchCV`), justificada por Bergstra y Bengio (2012). No se usó Optuna.
- **Validación**: 5 pliegues `StratifiedGroupKFold` por usuario sobre el 80 % de entrenamiento.
- **Métrica de optimización**: AUC-ROC.
- **Espacios de búsqueda previstos** (plan inicial; los espacios finales, ajustados tras una prueba rápida, están en `09_modelado_resultados.md`):
  - Regresión Logística: `C` ∈ [10⁻³, 10²] (escala logarítmica).
  - Random Forest: `n_estimators` ∈ [200, 600], `max_depth` ∈ {8, 12, 16, None}, `min_samples_leaf` ∈ [20, 200], `max_features` ∈ {`sqrt`, 0.3, 0.5}.
  - LightGBM: `num_leaves` ∈ [15, 127], `learning_rate` ∈ [0.01, 0.1], `min_child_samples` ∈ [20, 300], `subsample` ∈ [0.6, 1.0], `colsample_bytree` ∈ [0.5, 1.0], `reg_lambda` ∈ [0, 10], ajustando `n_estimators` como hiperparámetro.

Resultado: se probaron 12 configuraciones de Regresión Logística, 12 de Random Forest y 30 de LightGBM con `RandomizedSearchCV`. El espacio de LightGBM se desplazó hacia tasas de aprendizaje bajas (0.005–0.08) y hojas grandes (50–500 muestras) tras una prueba rápida que mostró sobreajuste. Los mejores hiperparámetros y el AUC de validación cruzada están en `09_modelado_resultados.md`.

### 6.1 Selección del umbral

Los modelos entregan probabilidades. Para las métricas que requieren clase (precisión, recall, F1, matriz de confusión), se elige el umbral que maximiza F1 en las predicciones *out-of-fold* del entrenamiento, y ese umbral se aplica sin cambios al conjunto de prueba.

---

## 7. Evaluación y comparación

- Métricas: AUC-ROC (principal), AUC-PR, precisión, recall y F1 de la clase positiva, matriz de confusión, tiempos de entrenamiento y de predicción (ver `06_revision_bibliografica.md`, sección 5).
- Líneas base de referencia: clasificador aleatorio (AUC-ROC = 0.5; AUC-PR = 0.061) y Regresión Logística.
- Visualizaciones estáticas previstas: curvas ROC comparadas, curvas precisión-recall comparadas, barras de métricas por modelo, matrices de confusión, importancia de variables y tiempos de cómputo.

Resultados en `09_modelado_resultados.md`. Además de lo previsto, se agregó un **ensamble** (promedio de percentiles de los tres modelos) y la **captura de recurrentes en el 10 % superior** como métrica de negocio.

---

## 8. Herramientas y recursos de cómputo

| Recurso | Detalle | Justificación |
|---|---|---|
| Equipo | CPU Intel Core Ultra 9 386H, 31.5 GB de RAM, Windows 11 | El procesamiento del registro de 55 millones de filas requiere memoria suficiente; no se necesita GPU para los modelos seleccionados. |
| Lenguaje | Python 3.12 en un entorno virtual (`.venv`) | Ecosistema estándar de ciencia de datos; versión con soporte estable de todas las bibliotecas usadas. |
| Manipulación de datos | pandas 3.0.6, NumPy 2.5.3, PyArrow 25.0.1 (formato parquet) | Lectura por fragmentos del log; parquet para guardar tablas intermedias de forma compacta y rápida. |
| Modelado | scikit-learn 1.9.1 (Regresión Logística, Random Forest, *pipelines*, validación), LightGBM 4.7.0 | Implementaciones de referencia de los algoritmos seleccionados (Pedregosa et al., 2011; Ke et al., 2017). |
| Persistencia de modelos | joblib | Guardar modelos entrenados para la aplicación. |
| Visualización estática | Matplotlib, Seaborn | Gráficas estáticas de los notebooks, continuidad con el EDA. |
| Aplicación | Streamlit 1.64.0 + Plotly 7.1.0 | Aplicación web en Python que reutiliza los modelos directamente; Plotly aporta gráficas interactivas. |
| Versionamiento | Git y GitHub | Requisito del curso y evidencia de contribuciones individuales. |

Versiones exactas fijadas en `requirements.txt`.

---

## 9. Aplicación (plan)

- **Tecnología**: Streamlit con gráficas Plotly.
- **Secciones previstas**:
  1. **Inicio**: el problema, los hallazgos clave del EDA y cómo se reflejan en los modelos.
  2. **Exploración de datos**: variables limpias y de modelado con filtros, distribuciones y cruces con la recompra.
  3. **Modelos**: rendimiento en prueba de un modelo o de todos (ROC, PR, matriz de confusión, importancia de variables), con controles para mostrar u ocultar cada gráfica.
  4. **Predicción**: el usuario ingresa un `user_id` y un `merchant_id` (la aplicación construye internamente las variables a partir de los agregados precalculados) o ingresa manualmente métricas de comportamiento; elige uno o todos los modelos y ve la probabilidad de recompra y la clase asignada.
- **Preprocesamiento transparente**: la aplicación aplica el mismo `Pipeline` usado en entrenamiento, sin que el usuario tenga que transformar datos.
- **Diseño**: paleta de colores definida según teoría del color (ver `10_aplicacion.md`).
