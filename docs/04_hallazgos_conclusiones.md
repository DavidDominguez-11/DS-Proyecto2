# Hallazgos y Conclusiones

Este documento resume los principales hallazgos del análisis exploratorio de datos realizado sobre el conjunto de datos de predicción de compradores recurrentes de la plataforma Tmall (Alibaba). Los resultados presentados aquí corresponden a los obtenidos en el notebook `notebooks/proyecto2_eda.ipynb`.

> **Nota**: Los hallazgos describen asociaciones observadas en los datos, no relaciones causales.

---

## 1. Hallazgos Principales

### 1.1 Desbalance Severo de la Variable Objetivo

- De los 260,864 pares usuario-vendedor en el conjunto de entrenamiento, solo 15,952 (6.1%) corresponden a compradores recurrentes (`label = 1`), mientras que 244,912 (93.9%) son no recurrentes (`label = 0`).
- Este desbalance es consistente con el fenómeno documentado en la literatura sobre compradores promocionales: la mayoría de clientes adquiridos durante eventos como el Double 11 no regresan.
- **Implicación**: Cualquier modelo predictivo futuro deberá abordar explícitamente el desbalance de clases mediante técnicas como sobremuestreo (SMOTE), submuestreo, o ponderación de clases.
- **Referencia**: Figura `01_distribucion_recompra.png`.

### 1.2 Perfil Demográfico y Recompra

- **Edad**: Los rangos de edad con mayor proporción de compradores recurrentes tienden a concentrarse entre 25 y 49 años, con `50+` consolidado como una sola categoría analítica. La proporción de usuarios con edad desconocida sigue siendo relevante (código 0 o NaN), por lo que la fortaleza de esta conclusión sigue siendo moderada.
- **Género**: Se observan diferencias modestas en la tasa de recompra entre géneros, aunque la proporción de género desconocido es considerable y diluye las diferencias observadas.
- **Referencia**: Figuras `06_label_vs_edad.png` y `07_label_vs_genero.png`.

### 1.3 Intensidad de Interacción como Indicador de Recompra

- Los compradores recurrentes tienden a presentar mayor cantidad de interacciones totales (`total_actions`) con el vendedor en comparación con los no recurrentes.
- Se observa una asociación positiva entre el número de compras (`purchase`), adiciones al carrito (`cart`) y favoritos (`favorite`) con la probabilidad de recompra.
- Los compradores recurrentes también muestran mayor número de días activos (`n_days`) en su interacción con el vendedor.
- **Referencia**: Figuras `08_label_vs_actividad_total.png`, `09_label_vs_tipos_accion.png`, `11_label_vs_dias_activos.png`.

### 1.4 Diversidad de Exploración

- Los compradores recurrentes tienden a explorar una mayor diversidad de productos (`n_items`), categorías (`n_cats`) y marcas (`n_brands`) dentro de un mismo vendedor; estas métricas se recalcularon de forma exacta por par usuario-vendedor.
- Esta mayor diversidad sugiere un interés más profundo en la oferta del vendedor, consistente con un perfil de cliente más comprometido.
- **Referencia**: Figura `10_label_vs_diversidad.png`.

### 1.5 Distribución de Tipos de Acción

- Los clics (action_type = 0) dominan la actividad, representando la gran mayoría de las interacciones.
- Las compras (action_type = 2) y adiciones al carrito (action_type = 1) son proporcionalmente menos frecuentes.
- La tasa de compra (`purchase_rate`) y la tasa de favoritos (`favorite_rate`) muestran asociaciones más claras con la recompra que la tasa de clics sola.
- **Referencia**: Figuras `04_histogramas_variables_numericas.png`, `09_label_vs_tipos_accion.png`.

### 1.6 Correlaciones entre Métricas de Actividad

- Se observan correlaciones positivas entre métricas de volumen: `total_actions`, `clicks`, `n_items` y `n_days`. Tras recalcular `n_items`, `n_cats`, `n_brands` y `n_days` de forma exacta, la estructura general del patrón se mantiene.
- Las métricas de proporción (tasas) muestran patrones de correlación diferentes: la `click_rate` tiene correlación negativa con `purchase_rate`, `cart_rate` y `favorite_rate`, lo cual es esperado dado que son proporciones complementarias.
- La correlación entre `purchase` y `label` es positiva pero moderada, lo que indica que la cantidad de compras por sí sola no es suficiente para predecir la recompra.
- **Referencia**: Figura `13_matriz_correlacion.png`.

### 1.7 Valores Atípicos

- Se observan valores extremos en variables como `total_actions`, `clicks` y `n_items`, correspondientes a usuarios con actividad excepcionalmente alta con un vendedor. La conservación de estos casos se mantiene porque reflejan comportamiento real y no un error de agregación.
- Estos valores atípicos no se eliminaron, ya que representan comportamientos reales (posiblemente usuarios automatizados o compradores de alto volumen) y su exclusión sin justificación introduciría sesgo.
- Se documentaron los percentiles y rangos para facilitar la detección y tratamiento en análisis posteriores.
- **Referencia**: Figuras `05_boxplots_variables_numericas.png`.

---

## 2. Limitaciones

1. **Desbalance de clases**: Con solo 6.1% de pares recurrentes, las estadísticas descriptivas y proporciones pueden estar dominadas por el grupo mayoritario (no recurrentes).

2. **Datos demográficos incompletos**: Una proporción significativa de usuarios tiene edad y/o género desconocidos (código 0/2 o NaN), lo que limita la capacidad de hacer inferencias demográficas robustas. Además, `age_range = 7` y `age_range = 8` deben interpretarse como `50+`, no como categorías faltantes.

3. **Sesgo de muestreo**: Los datos provienen exclusivamente de la plataforma Tmall durante un periodo que incluye el festival Double 11. Los patrones observados podrían no generalizarse a otros periodos o plataformas.

4. **Alcance temporal limitado**: El periodo de actividad registrado (mayo a noviembre) cubre aproximadamente 6 meses. Patrones de largo plazo o estacionales más amplios no se capturan.

5. **Ausencia de información monetaria**: Los datos no incluyen montos de transacción, lo que impide realizar análisis de valor monetario (componente M del análisis RFM).

6. **No se puede inferir causalidad**: Las asociaciones encontradas no implican relaciones causales. No es posible afirmar, por ejemplo, que explorar más productos *cause* la recompra; podría ser que los compradores recurrentes simplemente tengan un perfil de navegación más activo.

7. **Identificadores como seller_id/merchant_id**: La correspondencia entre `seller_id` en los logs y `merchant_id` en el entrenamiento requiere validación cuidadosa. El agregado exacto por bloques de `user_id` evita subestimar `n_items`, `n_cats`, `n_brands` y `n_days`.

8. **Posibles interacciones duplicadas en user_log**: No se verificó exhaustivamente la presencia de registros idénticos en el archivo de logs debido a su tamaño.

---

## 3. Siguientes Pasos

### 3.1 Ingeniería de Variables Adicional

- Construir variables temporales más sofisticadas: distribución de actividad pre/post Double 11, recencia de última interacción, velocidad de interacción (acciones por día).
- Crear métricas a nivel de vendedor (tamaño de base de clientes, tasa base de recompra del vendedor) y a nivel de usuario (actividad total en la plataforma, no solo con un vendedor específico).
- Explorar ratios como carrito-a-compra, favorito-a-compra, y concentración de actividad en el vendedor vs. plataforma.

### 3.2 Tratamiento del Desbalance de Clases

- Evaluar técnicas de sobremuestreo (SMOTE, Random Oversampling) y submuestreo para equilibrar las clases antes del entrenamiento de modelos.
- Considerar métricas de evaluación apropiadas para clases desbalanceadas: AUC-ROC, F1-score, precisión-recall en lugar de exactitud global.

### 3.3 Modelos de Clasificación

- Entrenar modelos de clasificación binaria como Regresión Logística, Random Forest, Gradient Boosting (XGBoost/LightGBM) para predecir la probabilidad de recompra.
- Utilizar validación cruzada estratificada para asegurar representación de ambas clases en cada pliegue.
- Implementar selección de variables basada en importancia del modelo.

### 3.4 Análisis de Segmentación

- Aplicar técnicas de clustering no supervisado para identificar arquetipos de compradores (leales, cazadores de ofertas, exploradores) basados en las métricas de actividad.
- Cruzar los segmentos identificados con la tasa de recompra para validar los perfiles.

> **Nota**: Los modelos predictivos y la segmentación avanzada no se implementan en este proyecto, que se centra exclusivamente en el análisis exploratorio de datos.

---

## 4. Tablas y Figuras de Referencia

| Figura/Tabla | Descripción | Ubicación |
|-------------|-------------|-----------|
| `01_distribucion_recompra.png` | Distribución de la variable objetivo | `outputs/figures/` |
| `02_distribucion_edad.png` | Distribución de rangos de edad | `outputs/figures/` |
| `03_distribucion_genero.png` | Distribución de género | `outputs/figures/` |
| `04_histogramas_variables_numericas.png` | Histogramas de variables numéricas derivadas | `outputs/figures/` |
| `05_boxplots_variables_numericas.png` | Diagramas de caja de variables numéricas | `outputs/figures/` |
| `06_label_vs_edad.png` | Recompra por rango de edad | `outputs/figures/` |
| `07_label_vs_genero.png` | Recompra por género | `outputs/figures/` |
| `08_label_vs_actividad_total.png` | Recompra vs. actividad total | `outputs/figures/` |
| `09_label_vs_tipos_accion.png` | Recompra vs. tipos de acción | `outputs/figures/` |
| `10_label_vs_diversidad.png` | Recompra vs. diversidad de exploración | `outputs/figures/` |
| `11_label_vs_dias_activos.png` | Recompra vs. días activos | `outputs/figures/` |
| `12_dispersion_compras_vs_acciones.png` | Dispersión compras vs. acciones totales | `outputs/figures/` |
| `13_matriz_correlacion.png` | Matriz de correlación de métricas derivadas | `outputs/figures/` |
| `14_analisis_faltantes_demograficos.png` | Análisis de valores faltantes demográficos | `outputs/figures/` |
| `estadisticas_descriptivas.csv` | Estadísticas descriptivas de variables numéricas | `outputs/tables/` |
| `tabla_analitica_resumen.csv` | Muestra de la tabla analítica construida | `outputs/tables/` |