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

- **Edad**: La tasa de recompra aumenta con la edad hasta el grupo 35–39 (7.00 %) y desciende ligeramente después (40–49: 6.83 %; `50+`: 6.18 %). El grupo 18–24 tiene la tasa más baja (4.93 %) y 25–29 (5.88 %) queda por debajo del promedio general (6.12 %). La edad es desconocida en el 21.9 % de los pares, por lo que la fortaleza de esta conclusión es moderada.
- **Género**: La tasa de recompra femenina (6.45 %) supera a la masculina (5.38 %). El género desconocido representa solo el 4.1 % de los pares, por lo que afecta poco a esta comparación.
- **Referencia**: Figuras `06_label_vs_edad.png` y `07_label_vs_genero.png`.

### 1.3 Intensidad de Interacción como Indicador de Recompra

- Los compradores recurrentes tienden a presentar mayor cantidad de interacciones totales (`total_actions`) con el vendedor en comparación con los no recurrentes.
- Se observa una asociación positiva de los clics (`clicks`), favoritos (`favorite`) y, en promedio, las compras (`purchase`) con la recompra. Las adiciones al carrito (`cart`) **no** muestran diferencia entre grupos (media 0.02 en ambos).
- Los compradores recurrentes también muestran mayor número de días activos (`n_days`) en su interacción con el vendedor.
- **Referencia**: Figuras `08_label_vs_actividad_total.png`, `09_label_vs_tipos_accion.png`, `11_label_vs_dias_activos.png`.

### 1.4 Diversidad de Exploración

- Los compradores recurrentes tienden a explorar una mayor diversidad de productos (`n_items`), categorías (`n_cats`) y marcas (`n_brands`) dentro de un mismo vendedor; estas métricas se recalcularon de forma exacta por par usuario-vendedor.
- Esta mayor diversidad sugiere un interés más profundo en la oferta del vendedor, consistente con un perfil de cliente más comprometido.
- **Referencia**: Figura `10_label_vs_diversidad.png`.

### 1.5 Distribución de Tipos de Acción

- Los clics (action_type = 0) dominan la actividad, representando la gran mayoría de las interacciones.
- Las compras (action_type = 2) y adiciones al carrito (action_type = 1) son proporcionalmente menos frecuentes.
- Las tasas por tipo de acción tienen correlaciones prácticamente nulas con la recompra (`click_rate` 0.023, `favorite_rate` 0.016, `cart_rate` −0.006, `purchase_rate` −0.028): importa más el volumen de interacción que su composición.
- **Referencia**: Figuras `04_histogramas_variables_numericas.png`, `09_label_vs_tipos_accion.png`.

### 1.6 Correlaciones entre Métricas de Actividad

- Se observan correlaciones positivas entre métricas de volumen: `total_actions`, `clicks`, `n_items` y `n_days`. Tras recalcular `n_items`, `n_cats`, `n_brands` y `n_days` de forma exacta, la estructura general del patrón se mantiene.
- Las métricas de proporción (tasas) muestran patrones de correlación diferentes: la `click_rate` tiene correlación negativa con `purchase_rate`, `cart_rate` y `favorite_rate`, lo cual es esperado dado que son proporciones complementarias.
- La correlación entre `purchase` y `label` es positiva pero débil (0.084), lo que indica que la cantidad de compras por sí sola no es suficiente para predecir la recompra.
- **Referencia**: Figura `13_matriz_correlacion.png`.

### 1.7 Valores Atípicos

- Se observan valores extremos en variables como `total_actions`, `clicks` y `n_items`, correspondientes a usuarios con actividad excepcionalmente alta con un vendedor. La conservación de estos casos se mantiene porque reflejan comportamiento real y no un error de agregación.
- Estos valores atípicos no se eliminaron, ya que representan comportamientos reales (posiblemente usuarios automatizados o compradores de alto volumen) y su exclusión sin justificación introduciría sesgo.
- Se documentaron los percentiles y rangos para facilitar la detección y tratamiento en análisis posteriores.
- **Referencia**: Figuras `05_boxplots_variables_numericas.png`.

---

### 1.8 Concentración Temporal en el Double 11

- El registro abarca del 11 de mayo al 12 de noviembre (186 días con actividad). La actividad es estable de mayo a octubre; las interacciones (sobre todo clics) crecen desde inicios de noviembre, pero las compras permanecen planas hasta el 11 de noviembre.
- El Double 11 concentra el **37.2 % de todas las compras** del periodo (~117 veces las compras de un día típico) y el 19.3 % de las interacciones.
- **Implicación**: conviene separar, en el modelado, la actividad del par durante el Double 11 de la actividad previa.
- **Referencia**: Figura `15_actividad_diaria.png`.

### 1.9 Pruebas Estadísticas y Tamaño del Efecto

- La prueba U de Mann-Whitney confirma diferencias significativas entre recurrentes y no recurrentes, pero con efectos pequeños: `n_items` (r = 0.20), `total_actions` y `n_cats` (0.17), `clicks` (0.15), `purchase` (0.14) y `n_days` (0.13). `cart` y `n_brands` tienen efecto prácticamente nulo.
- La correlación de Spearman confirma la dirección y magnitud de las de Pearson: las asociaciones individuales son débiles (≤ 0.10).
- La prueba χ² indica asociación significativa pero muy débil de la edad (V de Cramér = 0.026) y el género (V = 0.021) con la recompra.
- **Referencia**: Figura `16_correlacion_pearson_vs_spearman.png`; tablas `pruebas_mann_whitney.csv`, `pruebas_chi_cuadrado.csv`, `correlaciones_label.csv`.

### 1.10 Implicaciones para el Modelado

1. La señal está **repartida entre muchas variables de efecto pequeño** (|r| ≤ 0.10; efecto de Mann-Whitney ≤ 0.20). Esto justifica usar modelos no lineales que combinen variables (Random Forest, *boosting*) y compararlos contra una regresión logística.
2. `cart` y `n_brands` aportan poco (el carrito representa solo el 0.14 % de las acciones del registro); pueden mantenerse como variables, pero no se espera que sean relevantes.
3. La demografía aporta una señal débil y conviene incluirla como categórica.
4. El Double 11 domina las compras, así que conviene crear variables específicas de ese día y de la actividad previa con el vendedor.
5. El 25 % de filas repetidas en el registro hace que los conteos de acciones incluyan repeticiones del mismo día; las variables de días activos y de productos distintos son más robustas a este efecto.

---

## 2. Limitaciones

1. **Desbalance de clases**: Con solo 6.1% de pares recurrentes, las estadísticas descriptivas y proporciones pueden estar dominadas por el grupo mayoritario (no recurrentes).

2. **Datos demográficos incompletos**: Una proporción significativa de usuarios tiene edad y/o género desconocidos (código 0/2 o NaN), lo que limita la capacidad de hacer inferencias demográficas robustas. Además, `age_range = 7` y `age_range = 8` deben interpretarse como `50+`, no como categorías faltantes.

3. **Sesgo de muestreo**: Los datos provienen exclusivamente de la plataforma Tmall durante un periodo que incluye el festival Double 11. Los patrones observados podrían no generalizarse a otros periodos o plataformas.

4. **Alcance temporal limitado**: El periodo de actividad registrado (mayo a noviembre) cubre aproximadamente 6 meses. Patrones de largo plazo o estacionales más amplios no se capturan.

5. **Ausencia de información monetaria**: Los datos no incluyen montos de transacción, lo que impide realizar análisis de valor monetario (componente M del análisis RFM).

6. **No se puede inferir causalidad**: Las asociaciones encontradas no implican relaciones causales. No es posible afirmar, por ejemplo, que explorar más productos *cause* la recompra; podría ser que los compradores recurrentes simplemente tengan un perfil de navegación más activo.

7. **Identificadores como seller_id/merchant_id**: La correspondencia entre `seller_id` en los logs y `merchant_id` en el entrenamiento se validó (100 % de los pares de entrenamiento tienen actividad). El particionado por *hash* del par (`user_id`, `seller_id`) garantiza que `n_items`, `n_cats`, `n_brands` y `n_days` sean conteos exactos.

8. **Interacciones repetidas en user_log**: El 25.03 % de las filas del log (13,750,198) son idénticas a otra fila. Se conservaron como interacciones repetidas el mismo día, pero sin la hora no es posible distinguirlas de registros duplicados por error.

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
| `15_actividad_diaria.png` | Interacciones y compras por día (pico del Double 11) | `outputs/figures/` |
| `16_correlacion_pearson_vs_spearman.png` | Correlación de cada variable con la recompra: Pearson vs. Spearman | `outputs/figures/` |
| `estadisticas_descriptivas.csv` | Estadísticas descriptivas de variables numéricas | `outputs/tables/` |
| `tabla_analitica_resumen.csv` | Muestra de la tabla analítica construida | `outputs/tables/` |
| `actividad_diaria.csv` | Conteo diario de cada tipo de acción en el log completo | `outputs/tables/` |
| `correlaciones_label.csv` | Correlaciones de Pearson y Spearman con `label` | `outputs/tables/` |
| `pruebas_mann_whitney.csv` | Prueba U de Mann-Whitney y tamaño del efecto por variable | `outputs/tables/` |
| `pruebas_chi_cuadrado.csv` | Prueba χ² y V de Cramér para edad y género | `outputs/tables/` |