# Modelado, Ajuste de Hiperparámetros y Evaluación

Este documento describe el modelado (pasos 5 a 8 de `07_metodologia_modelado.md`), implementado en `notebooks/03_modelado.ipynb`: preprocesamiento, ajuste de hiperparámetros, selección del umbral, evaluación en el conjunto de prueba, comparación de modelos y exportación de los modelos para la aplicación.

---

## 1. Datos y referencias

- **Entrenamiento**: 208,691 pares (6.12 % positivos), con 5 pliegues de validación cruzada agrupados por usuario.
- **Prueba**: 52,173 pares (6.11 % positivos). Se usó una sola vez, al final.
- **Entradas**: 62 variables numéricas, 2 categóricas (edad y género) y `merchant_id` (para el *target encoding*).

| Referencia (prueba) | AUC-ROC | AUC-PR |
|---|---:|---:|
| Clasificador aleatorio | 0.500 | 0.061 |
| `m_repeat_buyer_rate_log` como puntaje | 0.614 | 0.096 |

## 2. Preprocesamiento

Todo el preprocesamiento vive dentro de un `Pipeline`, de modo que en cada pliegue se ajusta solo con los datos de entrenamiento de ese pliegue.

| Paso | Regresión Logística | Random Forest y LightGBM |
|---|---|---|
| 62 variables numéricas | `log1p` + estandarización | Sin transformar |
| Edad y género | *One-hot* | Códigos ordinales |
| `merchant_id` | *Target encoding* + estandarización | *Target encoding* |

**Target encoding sin fuga.** Se usa `TargetEncoder` de scikit-learn con suavizado automático hacia la media global:
- En `fit_transform` hace ajuste cruzado interno de 5 pliegues estratificados, así que cada fila recibe la tasa de recompra de su vendedor calculada sin su propia etiqueta.
- En `transform` (validación, prueba y aplicación) usa la tasa calculada con todo el entrenamiento.

Verificación:

| Target encoding | AUC-ROC |
|---|---:|
| En entrenamiento, **con fuga** (tasa calculada con la propia etiqueta) | 0.705 |
| En entrenamiento, fuera de pliegue | 0.651 |
| En prueba | **0.642** |

El AUC de prueba se parece al fuera de pliegue, no al de la versión con fuga: el ajuste cruzado da una estimación honesta. Por sí sola, la tasa de recompra del vendedor (0.642) ya supera a la mejor variable sin etiqueta (0.614).

## 3. Ajuste de hiperparámetros

- **Método**: `RandomizedSearchCV` (búsqueda aleatoria) optimizando AUC-ROC sobre los 5 pliegues predefinidos.
- **Configuraciones probadas**: 12 para la Regresión Logística, 12 para Random Forest y 30 para LightGBM, cada una evaluada en 5 pliegues.
- **Configuración fija**:
  - Regresión Logística: L2, `class_weight='balanced'`.
  - Random Forest: `class_weight='balanced_subsample'`.
  - LightGBM: `subsample_freq=1`.
- **Espacios de búsqueda**:
  - Regresión Logística: `C` ∈ [10⁻³, 10²] (log-uniforme).
  - Random Forest:
    - `n_estimators` ∈ [200, 500]
    - `max_depth` ∈ {10, 14, 18, 24, None}
    - `min_samples_leaf` ∈ [10, 200]
    - `max_features` ∈ {sqrt, 0.2, 0.3, 0.5}
    - `max_samples` ∈ [0.3, 0.8]
  - LightGBM:
    - `n_estimators` ∈ [200, 1500]
    - `learning_rate` ∈ [0.005, 0.08] (log-uniforme)
    - `num_leaves` ∈ [8, 96]
    - `min_child_samples` ∈ [50, 500]
    - `subsample` ∈ [0.6, 1.0]
    - `colsample_bytree` ∈ [0.4, 1.0]
    - `reg_lambda` ∈ [0, 10]
    - `reg_alpha` ∈ [0, 5]
    - `scale_pos_weight` ∈ {1, 3, 3.92, 15.35}
- **Ajuste del espacio de LightGBM**: una prueba rápida previa (una configuración por modelo, para verificar el código) mostró que una configuración con tasa de aprendizaje alta y hojas pequeñas sobreajustaba (AUC de entrenamiento 0.93 frente a 0.67 en validación). Por eso el espacio final favorece tasas de aprendizaje bajas y hojas grandes. **Transparencia**: esa prueba rápida también imprimió métricas del conjunto de prueba; el cambio del espacio se decidió solo con la brecha entrenamiento–validación, y los hiperparámetros finales se eligieron exclusivamente por validación cruzada.

| Modelo | AUC CV por defecto | AUC CV ajustado | Mejora | Desv. est. CV | AUC entrenamiento (defecto → ajustado) | Tiempo de búsqueda |
|---|---:|---:|---:|---:|---:|---:|
| Regresión Logística | 0.6911 | 0.6915 | +0.0004 | 0.0027 | 0.724 → 0.724 | 2.0 min |
| Random Forest | 0.6496 | 0.6903 | **+0.0407** | 0.0022 | **1.000** → 0.780 | 16.1 min |
| LightGBM | 0.6863 | **0.6931** | +0.0068 | 0.0012 | 0.791 → 0.777 | 14.2 min |

**Mejores hiperparámetros**
- **Regresión Logística**: `C` = 0.0013.
- **Random Forest**: `n_estimators` = 493, `max_depth` = None, `min_samples_leaf` = 167, `max_features` = 0.2, `max_samples` = 0.66.
- **LightGBM**: `n_estimators` = 1,021, `learning_rate` = 0.0078, `num_leaves` = 42, `min_child_samples` = 387, `subsample` = 0.61, `colsample_bytree` = 0.40, `reg_alpha` = 3.26, `reg_lambda` = 2.24, `scale_pos_weight` = 1.

**Interpretación**
- **Random Forest es el que más gana con el ajuste.** Por defecto memoriza el entrenamiento (AUC 1.000). Al exigir hojas grandes, submuestrear filas y variables, su AUC de entrenamiento baja a 0.780 y el de validación sube de 0.650 a 0.690.
- **LightGBM** gana con una tasa de aprendizaje baja, muchos árboles y una regularización fuerte. Dar más peso a la clase positiva no mejoró el AUC.
- **La Regresión Logística es insensible a `C`.** El mejor valor está cerca del límite inferior del rango, pero la ganancia es despreciable.
- **Las diferencias entre modelos ajustados (~0.003) son comparables a la variabilidad entre pliegues (0.001–0.003).**

## 4. Umbral de decisión y ensamble

- **Umbral**: para cada modelo se eligió el que maximiza F1 sobre las predicciones fuera de pliegue del entrenamiento, y se aplicó sin cambios a la prueba.
- **Ensamble**: promedia el **percentil** del puntaje de cada modelo dentro de su distribución fuera de pliegue (promedio de rangos). Se usan percentiles porque los pesos de clase ponen las probabilidades de cada modelo en escalas distintas.

| Modelo | AUC fuera de pliegue | Umbral | F1 fuera de pliegue |
|---|---:|---:|---:|
| Regresión Logística | 0.6915 | 0.636 | 0.212 |
| Random Forest | 0.6903 | 0.575 | 0.209 |
| LightGBM | 0.6931 | 0.107 | 0.215 |
| Ensamble | 0.6945 | 0.864 | 0.215 |

Los umbrales son muy distintos entre sí porque la Regresión Logística y Random Forest usan pesos de clase balanceados, lo que infla sus probabilidades, y LightGBM no.

## 5. Evaluación en el conjunto de prueba

| Modelo | AUC-ROC | AUC-PR | Precisión | Recall | F1 | Captura top 10 % | Exactitud | Entrenamiento | Predicción (52k) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Regresión Logística | 0.6892 | 0.1367 | 0.156 | 0.318 | 0.209 | 26.7 % | 0.853 | 1.2 s | 0.05 s |
| Random Forest | 0.6857 | 0.1343 | 0.146 | **0.358** | 0.208 | 26.9 % | 0.833 | 19.0 s | 0.24 s |
| LightGBM | 0.6893 | **0.1389** | 0.156 | 0.318 | 0.210 | 27.1 % | 0.853 | 4.8 s | 0.34 s |
| **Ensamble** | **0.6907** | 0.1388 | 0.154 | 0.336 | **0.211** | **27.3 %** | 0.846 | 25.0 s | 0.65 s |

Los tiempos corresponden a la ejecución final del notebook (CPU Intel Core Ultra 9 386H, 16 núcleos); varían entre ejecuciones según la carga del equipo (en una ejecución anterior la búsqueda de Random Forest tardó 25.8 min), mientras que las métricas y los hiperparámetros son idénticos por la semilla fija.

**Matrices de confusión** (prueba: 48,983 no recurrentes y 3,190 recurrentes)

| Modelo | VN | FP | FN | VP |
|---|---:|---:|---:|---:|
| Regresión Logística | 43,495 | 5,488 | 2,175 | 1,015 |
| Random Forest | 42,324 | 6,659 | 2,049 | 1,141 |
| LightGBM | 43,510 | 5,473 | 2,176 | 1,014 |
| Ensamble | 43,085 | 5,898 | 2,118 | 1,072 |

## 6. Importancia de las variables

- **`m_target_encoding`, la tasa de recompra del vendedor, es la variable más importante en los tres modelos.** Aporta ~20 % de la importancia en los árboles y tiene el mayor coeficiente en la Regresión Logística.
- **La segunda es la fidelidad histórica del vendedor sin etiqueta**: `m_repeat_buyer_rate_log` en los árboles (7–9 %) y `m_n_repeat_buyers` en la regresión.
- **Después vienen las variables del par**: diversidad (`p_n_items`, `p_n_cats`), compras del 11/11 (`p_purchase`) y antigüedad de la relación (`p_first_days_before`).
- **Coeficientes negativos en la Regresión Logística** (manteniendo las demás variables constantes):
  - `u_n_merchants`: los usuarios que reparten su actividad entre muchos vendedores son menos fieles a cada uno.
  - `m_clicks` y `m_actions`: los vendedores con mucho tráfico de navegación retienen proporcionalmente menos.
- **Las variables demográficas tienen un peso bajo.**

## 7. Conclusiones y selección del modelo

1. **Se cumple la meta.** Todos los modelos obtienen un AUC-ROC en prueba de **0.686–0.691**, por encima de la meta de 0.65, del clasificador aleatorio y de la mejor variable individual (0.614). El AUC-PR (0.134–0.139) es más del doble de la prevalencia.
2. **Valor práctico.** Contactar al 10 % de compradores con mayor puntaje alcanza al **~27 % de los recurrentes**, 2.7 veces más que al azar. Con el umbral de F1, la precisión (~15 %) es 2.5 veces la tasa base.
3. **El problema es difícil.** Un F1 de ~0.21 y un AUC cercano a 0.70 coinciden con lo reportado para la solución ganadora de la competencia (Liu et al., 2016). La exactitud (83–85 %) no se usa para comparar porque es menor que la del clasificador trivial (93.9 %).
4. **Los algoritmos rinden prácticamente igual.** Las diferencias (≤ 0.005 de AUC) son del orden del ruido de la validación cruzada. El límite lo pone la información disponible, no el algoritmo.
5. **Selección.**
   - **LightGBM es el modelo principal**: mejor AUC en validación cruzada (0.693), la menor variabilidad entre pliegues, el mejor AUC-PR en prueba, entrenamiento rápido y robustez frente a variables sesgadas.
   - El **Ensamble** tiene el mejor AUC-ROC en prueba, pero la ganancia (+0.001) no justifica mantener tres modelos.
   - La **Regresión Logística** es la alternativa interpretable y la más rápida.
   - **Random Forest** es el más costoso de ajustar y el de menor AUC, aunque tiene el mayor recall con su umbral.
6. **Hallazgo de negocio.** Lo que más predice la recompra es **el vendedor**: su tasa histórica de recompra y la fidelidad de su clientela. Después viene la profundidad y la antigüedad de la relación del usuario con ese vendedor.

## 8. Archivos generados

| Archivo | Contenido |
|---|---|
| `notebooks/03_modelado.ipynb` | Notebook ejecutado (~45 min en CPU de 16 núcleos) |
| `outputs/models/modelo_lr.joblib`, `modelo_rf.joblib`, `modelo_lgbm.joblib` | `Pipeline` completos (preprocesamiento y modelo) |
| `outputs/models/referencia_ensamble.npz` | Distribuciones fuera de pliegue para calcular percentiles del ensamble |
| `outputs/models/predicciones_prueba.parquet` | Etiqueta y puntaje de cada modelo para los 52,173 pares de prueba (gráficas interactivas de la aplicación) |
| `outputs/models/metadata.json` | Variables, umbrales, hiperparámetros y métricas de cada modelo |
| `outputs/tables/ajuste_hiperparametros.csv` | Comparación entre configuración por defecto y ajustada |
| `outputs/tables/cv_busqueda_{lr,rf,lgbm}.csv` | Todas las configuraciones probadas con su AUC de validación y entrenamiento |
| `outputs/tables/comparacion_modelos.csv` | Métricas completas en prueba y tiempos |
| `outputs/tables/importancia_variables.csv` | Importancia de cada variable en los tres modelos |
| `outputs/figures/18_ajuste_hiperparametros.png` | AUC por defecto frente a ajustado (validación y entrenamiento) |
| `outputs/figures/19_curvas_roc_pr.png` | Curvas ROC y precisión-recall en prueba |
| `outputs/figures/20_metricas_modelos.png` | Barras de métricas por modelo |
| `outputs/figures/21_matrices_confusion.png` | Matrices de confusión |
| `outputs/figures/22_curva_ganancia.png` | Curva de ganancia acumulada |
| `outputs/figures/23_tiempos_modelos.png` | Tiempos de búsqueda, entrenamiento y predicción |
| `outputs/figures/24_importancia_variables.png` | 15 variables más importantes por modelo |
