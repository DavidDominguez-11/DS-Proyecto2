# Resultados e Interpretación del Análisis Exploratorio

## 1. Nota metodológica breve

La unidad de análisis del proyecto es el par usuario-vendedor. Las métricas de actividad, diversidad y permanencia se calcularon de forma exacta por `(user_id, merchant_id)`, conservando una sola observación por cada combinación en la tabla analítica final. Los resultados que se presentan a continuación describen asociaciones observadas en los datos y no permiten establecer causalidad.

## 2. Composición del conjunto de entrenamiento

La tabla analítica final contiene 260,864 observaciones y 18 variables: 3 columnas del conjunto de entrenamiento (`user_id`, `merchant_id`, `label`), 2 variables demográficas (`age_range`, `gender`), 9 métricas de actividad y diversidad (`total_actions`, `clicks`, `cart`, `purchase`, `favorite`, `n_items`, `n_cats`, `n_brands`, `n_days`) y 4 tasas derivadas (`click_rate`, `cart_rate`, `purchase_rate`, `favorite_rate`).

La distribución de `label` muestra un desbalance severo:

| label | Frecuencia | Porcentaje |
|---|---:|---:|
| No recurrente | 244,912 | 93.88% |
| Recurrente | 15,952 | 6.12% |

Interpretación: el conjunto está fuertemente dominado por pares no recurrentes, por lo que cualquier lectura posterior debe considerar que la clase recurrente es minoritaria. Esta distribución se resume en [01_distribucion_recompra.png](../outputs/figures/01_distribucion_recompra.png) y en [resumen_columnas_train.csv](../outputs/tables/resumen_columnas_train.csv), junto con la [tabla analítica resumida](../outputs/tables/tabla_analitica_resumen.csv).

## 3. Resultados demográficos

### 3.1 Edad

La edad se recodificó siguiendo la guía oficial: `0` y el valor original `NaN` se trataron como desconocido; los códigos `7` y `8` se consolidaron en la categoría analítica `50+`.

| Rango de edad | No recurrente | Recurrente | Total | Tasa de recompra |
|---|---:|---:|---:|---:|
| `<18` | 13 | 0 | 13 | 0.00% |
| `18-24` | 29,495 | 1,531 | 31,026 | 4.93% |
| `25-29` | 65,289 | 4,080 | 69,369 | 5.88% |
| `30-34` | 47,791 | 3,444 | 51,235 | 6.72% |
| `35-39` | 23,825 | 1,793 | 25,618 | 7.00% |
| `40-49` | 20,218 | 1,483 | 21,701 | 6.83% |
| `50+` | 4,541 | 299 | 4,840 | 6.18% |
| `Desconocido` | 53,740 | 3,322 | 57,062 | 5.82% |
| `Total` | 244,912 | 15,952 | 260,864 | 6.12% |

Interpretación: el grupo con mayor tasa de recompra es `35-39` con 7.00%, seguido de `40-49` con 6.83% y `30-34` con 6.72%. La categoría `50+` no debe interpretarse como desconocida, sino como una consolidación de los códigos 7 y 8; en este conjunto representa 4,840 pares, equivalentes al 1.86% del total. La categoría `18-24` presenta una tasa más baja, 4.93%. El grupo desconocido es numeroso, con 57,062 observaciones, por lo que limita la precisión de cualquier lectura demográfica fina. Esta evidencia se observa en [02_distribucion_edad.png](../outputs/figures/02_distribucion_edad.png), [06_label_vs_edad.png](../outputs/figures/06_label_vs_edad.png) y [frecuencia_edad_label.csv](../outputs/tables/frecuencia_edad_label.csv).

### 3.2 Género

El código `2` y el valor original `NaN` se trataron como desconocido.

| Género | No recurrente | Recurrente | Total | Tasa de recompra |
|---|---:|---:|---:|---:|
| Femenino | 165,027 | 11,387 | 176,414 | 6.45% |
| Masculino | 69,787 | 3,969 | 73,756 | 5.38% |
| Desconocido | 10,098 | 596 | 10,694 | 5.57% |
| Total | 244,912 | 15,952 | 260,864 | 6.12% |

Interpretación: la diferencia entre femenino y masculino existe, pero es moderada. El grupo femenino concentra 176,414 observaciones y muestra una tasa de recompra de 6.45%, mientras que el grupo masculino tiene 5.38%. La categoría desconocida representa 10,694 pares y se ubica en 5.57%, por lo que su lectura debe ser prudente. La distribución y el cruce con `label` se visualizan en [03_distribucion_genero.png](../outputs/figures/03_distribucion_genero.png), [07_label_vs_genero.png](../outputs/figures/07_label_vs_genero.png) y [frecuencia_genero_label.csv](../outputs/tables/frecuencia_genero_label.csv).

## 4. Resultados de comportamiento e interacción

### 4.1 Actividad total

| label | Media | Mediana | Q1 | Q3 | Máximo |
|---|---:|---:|---:|---:|---:|
| No recurrente | 10.4 | 6.0 | 3.0 | 11.0 | 1,269.0 |
| Recurrente | 17.1 | 8.0 | 4.0 | 18.0 | 3,918.0 |

Interpretación: los pares recurrentes presentan una intensidad de actividad claramente mayor. Su media es 17.1 frente a 10.4, la mediana sube de 6 a 8 y el cuartil superior pasa de 11 a 18. La diferencia también se refleja en los valores extremos, donde el máximo recurrente alcanza 3,918 acciones. La figura [08_label_vs_actividad_total.png](../outputs/figures/08_label_vs_actividad_total.png) y [estadisticas_descriptivas.csv](../outputs/tables/estadisticas_descriptivas.csv) sostienen esta lectura.

### 4.2 Tipos de acción

| label | Clicks | Carrito | Compra | Favorito |
|---|---:|---:|---:|---:|
| No recurrente | 8.7026 | 0.0239 | 1.3207 | 0.3675 |
| Recurrente | 14.8254 | 0.0209 | 1.6232 | 0.6792 |

| label | Mediana clicks | Mediana carrito | Mediana compra | Mediana favorito |
|---|---:|---:|---:|---:|
| No recurrente | 4.0 | 0.0 | 1.0 | 0.0 |
| Recurrente | 6.0 | 0.0 | 1.0 | 0.0 |

Interpretación: las diferencias más visibles aparecen en `clicks` y `favorite`. Los recurrentes promedian 14.8254 clics frente a 8.7026, y 0.6792 favoritos frente a 0.3675. En cambio, `cart` casi no cambia entre grupos, con promedios muy bajos y mediana cero en ambos casos. `purchase` aumenta de 1.3207 a 1.6232, pero la mediana permanece en 1, lo que indica una diferencia real aunque no drástica. Esta comparación se apoya en [09_label_vs_tipos_accion.png](../outputs/figures/09_label_vs_tipos_accion.png) y [medias_acciones_por_label.csv](../outputs/tables/medias_acciones_por_label.csv).

### 4.3 Diversidad de exploración

| label | n_items | n_cats | n_brands | n_days |
|---|---:|---:|---:|---:|
| No recurrente | 4.18 | 1.83 | 1.11 | 1.9 |
| Recurrente | 7.47 | 2.63 | 1.14 | 2.4 |

Interpretación: los recurrentes exploran más y durante más días. En términos de diversidad, pasan de 4.18 ítems únicos a 7.47, de 1.83 categorías a 2.63 y de 1.9 días activos a 2.4. `n_items`, `n_cats`, `n_brands` y `n_days` son conteos únicos globales exactos por par usuario-vendedor, calculados sobre toda la evidencia disponible para cada combinación. La figura [10_label_vs_diversidad.png](../outputs/figures/10_label_vs_diversidad.png) y [tabla_analitica_resumen.csv](../outputs/tables/tabla_analitica_resumen.csv) documentan esta diferencia.

### 4.4 Días activos

| label | Media | Mediana | Q1 | Q3 | Máximo |
|---|---:|---:|---:|---:|---:|
| No recurrente | 1.9 | 1.0 | 1.0 | 2.0 | 56.0 |
| Recurrente | 2.4 | 2.0 | 1.0 | 3.0 | 53.0 |

Interpretación: la distribución de `n_days` muestra que los recurrentes tienden a extender su interacción durante más días. La mediana sube de 1 a 2 y el cuartil superior de 2 a 3. Los máximos altos en ambos grupos confirman que existen algunos pares con actividad sostenida en ventanas largas, aunque son casos extremos. La evidencia se resume en [11_label_vs_dias_activos.png](../outputs/figures/11_label_vs_dias_activos.png) y en [estadisticas_descriptivas.csv](../outputs/tables/estadisticas_descriptivas.csv).

## 5. Distribuciones, outliers y faltantes

Las variables numéricas muestran un sesgo claro a la derecha. En los histogramas se concentra gran parte de la masa en valores bajos, mientras que los boxplots revelan colas largas y valores extremos. Esto es coherente con la naturaleza del comportamiento de compra: la mayoría de los pares interactúa poco, pero una fracción menor registra mucha actividad.

| Variable | Q1 | Q3 | IQR | Límite superior | Outliers | % outliers |
|---|---:|---:|---:|---:|---:|---:|
| total_actions | 3.0 | 12.0 | 9.0 | 25.5 | 22,834 | 8.75% |
| clicks | 2.0 | 10.0 | 8.0 | 22.0 | 23,229 | 8.90% |
| cart | 0.0 | 0.0 | 0.0 | 0.0 | 4,619 | 1.77% |
| purchase | 1.0 | 1.0 | 0.0 | 1.0 | 53,803 | 20.62% |
| favorite | 0.0 | 0.0 | 0.0 | 0.0 | 48,210 | 18.48% |
| n_items | 1.0 | 4.0 | 3.0 | 8.5 | 31,959 | 12.25% |
| n_cats | 1.0 | 2.0 | 1.0 | 3.5 | 29,461 | 11.29% |
| n_brands | 1.0 | 1.0 | 0.0 | 1.0 | 22,497 | 8.62% |
| n_days | 1.0 | 2.0 | 1.0 | 3.5 | 24,921 | 9.55% |

Interpretación: los outliers son numerosos en varias variables, en especial `purchase` y `favorite`, pero se conservaron porque representan comportamientos reales de alta intensidad y no necesariamente errores. En particular, las colas largas son esperables cuando se analizan interacciones de usuarios con vendedores, ya que unos pocos pares acumulan mucha más actividad que el resto. Esta lectura se respalda con [04_histogramas_variables_numericas.png](../outputs/figures/04_histogramas_variables_numericas.png), [05_boxplots_variables_numericas.png](../outputs/figures/05_boxplots_variables_numericas.png) y [analisis_outliers.csv](../outputs/tables/analisis_outliers.csv).

La disponibilidad de variables demográficas sugiere una asociación leve con la recompra, pero no una diferencia fuerte. Para edad, los pares con edad conocida muestran 6.2% de recurrentes, mientras que los de edad desconocida muestran 5.8%. Para género, los pares con género conocido registran 6.1% de recurrentes y los desconocidos 5.6%. Esto no permite afirmar que la ausencia de información sea MNAR; solo indica que la recompra varía ligeramente entre los subgrupos observados. La evidencia se presenta en [14_analisis_faltantes_demograficos.png](../outputs/figures/14_analisis_faltantes_demograficos.png) y en [resumen_columnas_user_info.csv](../outputs/tables/resumen_columnas_user_info.csv).

## 6. Correlaciones

La matriz de correlación se construyó solo con variables analíticas; no se incluyeron identificadores. Las asociaciones más altas con `label` son positivas y modestas: `n_cats` (0.103), `n_items` (0.099), `purchase` (0.084), `total_actions` (0.081), `n_days` (0.078), `clicks` (0.077) y `favorite` (0.052). Las tasas derivadas muestran correlaciones pequeñas, como `click_rate` (0.023), `favorite_rate` (0.016), `n_brands` (0.015) y `cart_rate` (-0.006). `purchase_rate` aparece con una correlación levemente negativa (-0.028), lo que es compatible con el hecho de que estas tasas son composicionales y no independientes entre sí.

Interpretación: no hay relaciones lineales fuertes con la etiqueta, pero sí un patrón consistente donde la recompra se asocia con mayor intensidad, mayor diversidad de navegación y mayor permanencia. La evidencia se observa en [13_matriz_correlacion.png](../outputs/figures/13_matriz_correlacion.png).

## 7. Interpretación integrada

En conjunto, los datos describen a un comprador recurrente como un par usuario-vendedor con mayor volumen de interacción, mayor exploración de ítems y categorías, y mayor continuidad temporal en el uso. La diferencia no aparece como un salto extremo en una sola métrica, sino como un patrón acumulado: más clics, más compras observadas, más favoritos, más ítems distintos y más días activos.

La señal demográfica existe, pero es más tenue que la conductual. La tasa de recompra es algo mayor en el grupo femenino y en los rangos de edad intermedios, especialmente entre 30 y 39 años, aunque la categoría desconocida sigue siendo amplia en edad y género. Por ello, la interpretación demográfica debe ser prudente y no sobreajustarse a diferencias pequeñas.

El análisis también muestra que la distribución de las variables es asimétrica y que existen numerosos outliers, lo cual es coherente con un comportamiento de consumo heterogéneo. En términos prácticos, el perfil recurrente parece estar más cerca de un usuario que explora con más amplitud y regresa durante más días, pero esa descripción sigue siendo probabilística y no causal. Las evidencias detalladas anteriores sostienen esa lectura sin justificar generalizaciones más fuertes.

## 8. Figuras y tablas utilizadas

| Evidencia | Resultado que sustenta | Ubicación |
|---|---|---|
| Distribución de recompra | Desbalance de clases entre recurrentes y no recurrentes | [outputs/figures/01_distribucion_recompra.png](../outputs/figures/01_distribucion_recompra.png) |
| Distribución de edad | Estructura general de la muestra por rangos de edad | [outputs/figures/02_distribucion_edad.png](../outputs/figures/02_distribucion_edad.png) |
| Distribución de género | Estructura general de la muestra por género | [outputs/figures/03_distribucion_genero.png](../outputs/figures/03_distribucion_genero.png) |
| Histogramas numéricos | Sesgo a la derecha en variables de actividad y diversidad | [outputs/figures/04_histogramas_variables_numericas.png](../outputs/figures/04_histogramas_variables_numericas.png) |
| Boxplots numéricos | Presencia de colas largas y outliers | [outputs/figures/05_boxplots_variables_numericas.png](../outputs/figures/05_boxplots_variables_numericas.png) |
| `label` vs edad | Tasa de recompra por rango de edad | [outputs/figures/06_label_vs_edad.png](../outputs/figures/06_label_vs_edad.png) |
| `label` vs género | Tasa de recompra por género | [outputs/figures/07_label_vs_genero.png](../outputs/figures/07_label_vs_genero.png) |
| `label` vs actividad total | Diferencias en volumen de actividad | [outputs/figures/08_label_vs_actividad_total.png](../outputs/figures/08_label_vs_actividad_total.png) |
| `label` vs tipos de acción | Comparación de clicks, carrito, compra y favorito | [outputs/figures/09_label_vs_tipos_accion.png](../outputs/figures/09_label_vs_tipos_accion.png) |
| `label` vs diversidad | Diferencias en diversidad de exploración | [outputs/figures/10_label_vs_diversidad.png](../outputs/figures/10_label_vs_diversidad.png) |
| `label` vs días activos | Permanencia temporal de la interacción | [outputs/figures/11_label_vs_dias_activos.png](../outputs/figures/11_label_vs_dias_activos.png) |
| Dispersión compras vs acciones | Relación visual entre intensidad y compras | [outputs/figures/12_dispersion_compras_vs_acciones.png](../outputs/figures/12_dispersion_compras_vs_acciones.png) |
| Matriz de correlación | Relaciones lineales entre variables analíticas | [outputs/figures/13_matriz_correlacion.png](../outputs/figures/13_matriz_correlacion.png) |
| Faltantes demográficos | Asociación entre disponibilidad de edad/género y `label` | [outputs/figures/14_analisis_faltantes_demograficos.png](../outputs/figures/14_analisis_faltantes_demograficos.png) |
| Resumen del entrenamiento | Número de observaciones y variables base | [outputs/tables/resumen_columnas_train.csv](../outputs/tables/resumen_columnas_train.csv) |
| Resumen de información de usuario | Disponibilidad de edad y género | [outputs/tables/resumen_columnas_user_info.csv](../outputs/tables/resumen_columnas_user_info.csv) |
| Tabla analítica resumida | Estructura final de la base analítica | [outputs/tables/tabla_analitica_resumen.csv](../outputs/tables/tabla_analitica_resumen.csv) |
| Estadísticas descriptivas | Medias, medianas, cuartiles y máximos | [outputs/tables/estadisticas_descriptivas.csv](../outputs/tables/estadisticas_descriptivas.csv) |
| Frecuencia de edad por `label` | Distribución y tasa de recompra por edad | [outputs/tables/frecuencia_edad_label.csv](../outputs/tables/frecuencia_edad_label.csv) |
| Frecuencia de género por `label` | Distribución y tasa de recompra por género | [outputs/tables/frecuencia_genero_label.csv](../outputs/tables/frecuencia_genero_label.csv) |
| Promedios de acciones por `label` | Comparación entre recurrentes y no recurrentes | [outputs/tables/medias_acciones_por_label.csv](../outputs/tables/medias_acciones_por_label.csv) |
| Análisis de outliers | Conteo y porcentaje de valores atípicos | [outputs/tables/analisis_outliers.csv](../outputs/tables/analisis_outliers.csv) |
