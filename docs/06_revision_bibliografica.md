# Revisión Bibliográfica y Selección de Algoritmos

Este documento corresponde a las actividades 1 y 2 de la guía *Proyecto 2 — Resultados*: revisar qué algoritmos de aprendizaje automático se han utilizado para resolver problemas similares y, con base en esa revisión, seleccionar los algoritmos que se usarán en el proyecto.

> **Estado de las referencias**: todas las referencias listadas en la sección 6 deben ser verificadas por el grupo (DOI, año, páginas) en Google Scholar, IEEE Xplore, ACM Digital Library o los recursos de la biblioteca UVG antes de la entrega. La columna *Verificada* de la tabla de la sección 6 se actualizará conforme se confirmen. Además de los datos bibliográficos, conviene contrastar los resúmenes de la sección 2 con el *abstract* de cada artículo, en especial los detalles específicos de Liu et al. (2016) (modelos comparados y AUC final), Buckinx y Van den Poel (2005) y Coussement y Van den Poel (2008).

---

## 1. Naturaleza del problema

La predicción de compradores recurrentes es un problema de **clasificación binaria supervisada** sobre datos tabulares:

- **Unidad de observación**: el par (usuario, vendedor) de un comprador nuevo adquirido durante el Double 11.
- **Variable objetivo**: `label` (1 = vuelve a comprar al mismo vendedor en los 6 meses siguientes; 0 = no vuelve).
- **Salida esperada**: una probabilidad de recompra, no solo una clase. La competencia original evalúa con **AUC-ROC**.
- **Características del problema** (confirmadas en el EDA):
  - Desbalance severo: 6.12 % de clase positiva.
  - Variables de comportamiento con distribuciones muy sesgadas y outliers numerosos.
  - Correlaciones lineales individuales débiles con la etiqueta (máximo |r| ≈ 0.10), lo que sugiere relaciones no lineales y efectos de interacción.
  - Información distribuida en tres niveles: usuario, vendedor y par usuario-vendedor.

Estas características orientan la revisión hacia: (a) modelos de predicción de recompra/abandono (*churn*) en comercio electrónico y retail, (b) métodos de ensamble basados en árboles para datos tabulares, y (c) técnicas de evaluación y tratamiento para clases desbalanceadas.

---

## 2. Trabajos relacionados

### 2.1 Predicción de compradores recurrentes en Tmall (el mismo problema)

Liu et al. (2016) describen la solución ganadora de la competencia *Repeat Buyers Prediction* (IJCAI-15), organizada con los mismos datos de Tmall utilizados en este proyecto. Sus aportes principales son:

- **Ingeniería de variables en varios niveles**: variables de usuario, de vendedor, de par usuario-vendedor y de categoría/marca, además de variables temporales (actividad cercana al Double 11) y de similitud usuario-vendedor. Reportan que la ingeniería de variables tuvo más impacto que la elección del algoritmo.
- **Modelos**: compararon Regresión Logística, Random Forest, Factorization Machines y Gradient Boosted Decision Trees (GBDT). Los modelos basados en árboles con *boosting* ofrecieron el mejor rendimiento individual.
- **Ensamble**: la solución final combinó varios modelos, obteniendo un AUC cercano a 0.70 en el conjunto de prueba de la competencia.

**Implicación para este proyecto**: confirma que el problema es difícil (un AUC de ~0.70 es competitivo) y que conviene (1) construir variables en múltiples niveles y (2) comparar un modelo lineal base contra ensambles de árboles.

### 2.2 Predicción de abandono y recompra de clientes (*churn*)

La predicción de recompra es la contraparte de la predicción de abandono en contextos no contractuales (el cliente puede dejar de comprar sin avisar):

- **Buckinx y Van den Poel (2005)** modelan la deserción parcial de clientes leales en retail no contractual usando Regresión Logística, Redes Neuronales y Random Forest, con variables de tipo RFM (recencia, frecuencia, monto). Encuentran que las variables de comportamiento histórico son los predictores más fuertes.
- **Lemmens y Croux (2006)** muestran que los ensambles de árboles (*bagging* y *boosting*) mejoran sustancialmente la capacidad predictiva frente a la regresión logística en predicción de *churn*, y discuten cómo corregir el sesgo introducido por el desbalance de clases.
- **Neslin et al. (2006)** comparan decenas de enfoques de modelado de *churn* presentados en un torneo académico y concluyen que la regresión logística y los árboles de decisión son competitivos, pero que el método de estimación y las variables utilizadas generan diferencias relevantes en el beneficio económico.
- **Coussement y Van den Poel (2008)** comparan Máquinas de Soporte Vectorial con Regresión Logística y Random Forest en servicios de suscripción; Random Forest resultó superior, y las SVM fueron sensibles a la selección de parámetros.
- **Verbeke et al. (2012)** evalúan múltiples clasificadores con una medida orientada a beneficio (*profit-driven*) y resaltan que, además de la precisión, importan la interpretabilidad y la utilidad del modelo para la toma de decisiones de retención.

**Implicación para este proyecto**: la literatura de *churn* respalda usar la Regresión Logística como línea base interpretable y los ensambles de árboles como candidatos de mayor rendimiento, y recomienda métricas que reflejen el valor práctico del modelo (por ejemplo, identificar a los clientes con mayor probabilidad de recompra).

### 2.3 Algoritmos de ensamble para datos tabulares

- **Random Forest (Breiman, 2001)**: combina muchos árboles entrenados sobre muestras *bootstrap* y subconjuntos aleatorios de variables. Reduce la varianza, captura no linealidades e interacciones, es robusto a outliers y a variables sesgadas, y requiere poco preprocesamiento.
- **Gradient Boosting (Friedman, 2001)**: construye árboles de forma secuencial, donde cada árbol corrige los errores residuales de los anteriores minimizando una función de pérdida mediante descenso de gradiente.
- **XGBoost (Chen y Guestrin, 2016)**: implementación de *gradient boosting* escalable con regularización, manejo nativo de valores faltantes y paralelización. Ha sido ampliamente utilizado en competencias de datos tabulares.
- **LightGBM (Ke et al., 2017)**: variante de *gradient boosting* que utiliza histogramas, crecimiento de árboles por hoja (*leaf-wise*), *Gradient-based One-Side Sampling* (GOSS) y *Exclusive Feature Bundling* (EFB). Es considerablemente más rápido y eficiente en memoria que otras implementaciones con precisión similar o superior, lo cual es relevante con ~260,000 observaciones y decenas de variables.

### 2.4 Aprendizaje con clases desbalanceadas

- **He y Garcia (2009)** revisan los enfoques para datos desbalanceados: remuestreo (sobremuestreo, submuestreo), métodos sensibles al costo (ponderación de clases) y ajuste del umbral de decisión. Advierten que la exactitud (*accuracy*) es engañosa cuando una clase es minoritaria.
- **Chawla et al. (2002)** proponen SMOTE, que genera ejemplos sintéticos de la clase minoritaria por interpolación entre vecinos.
- **Fawcett (2006)** explica el análisis ROC y el AUC como medida de la capacidad de ordenamiento de un clasificador, independiente del umbral y de la proporción de clases.
- **Saito y Rehmsmeier (2015)** muestran que, con clases desbalanceadas, la curva precisión-exhaustividad (*precision-recall*) es más informativa que la curva ROC, porque refleja directamente el rendimiento sobre la clase minoritaria.

### 2.5 Ajuste de hiperparámetros y validación

- **Kohavi (1995)** recomienda la validación cruzada estratificada de *k* pliegues (k = 10 o k = 5) para estimar el rendimiento y seleccionar modelos con menor sesgo y varianza.
- **Bergstra y Bengio (2012)** demuestran que la búsqueda aleatoria de hiperparámetros es más eficiente que la búsqueda en malla (*grid search*) cuando solo algunos hiperparámetros son relevantes.
- **Akiba et al. (2019)** presentan Optuna, un marco de optimización de hiperparámetros basado en búsqueda bayesiana secuencial (TPE) con poda de ensayos poco prometedores.

### 2.6 Interpretabilidad

- **Lundberg y Lee (2017)** proponen SHAP, un método basado en valores de Shapley para explicar la contribución de cada variable a cada predicción. Es útil para comunicar qué variables impulsan la probabilidad de recompra, tanto en el informe como en la aplicación.

---

## 3. Síntesis de la revisión

| Enfoque | Uso en la literatura revisada | Fortalezas | Debilidades |
|---|---|---|---|
| Regresión Logística | Línea base en Liu et al. (2016), Buckinx y Van den Poel (2005), Neslin et al. (2006) | Interpretable, rápida, probabilidades bien calibradas, sirve como referencia | Solo captura relaciones lineales en el espacio logit; sensible a escalas y sesgo de variables |
| Random Forest | Buckinx y Van den Poel (2005), Coussement y Van den Poel (2008), Liu et al. (2016) | No lineal, robusto a outliers, poco preprocesamiento, importancia de variables | Modelos pesados en memoria, probabilidades menos calibradas, más lento en predicción |
| Gradient Boosting (XGBoost / LightGBM) | Liu et al. (2016), Lemmens y Croux (2006), Chen y Guestrin (2016), Ke et al. (2017) | Mejor rendimiento típico en datos tabulares, maneja faltantes y desbalance vía pesos | Más hiperparámetros, riesgo de sobreajuste si no se regula |
| SVM | Coussement y Van den Poel (2008) | Buen desempeño con kernels | Escala mal a cientos de miles de observaciones; sensible a parámetros |
| Redes neuronales / Factorization Machines | Buckinx y Van den Poel (2005), Liu et al. (2016) | Capturan interacciones complejas | Sin ventaja clara sobre boosting en datos tabulares de este tamaño; mayor costo de ajuste |
| Ensamble de modelos | Liu et al. (2016) | Combina fortalezas, suele mejorar el AUC | Menor interpretabilidad y mayor complejidad |

---

## 4. Algoritmos seleccionados

Con base en la revisión y en las características del problema, se seleccionan los siguientes algoritmos:

### 4.1 Regresión Logística — modelo base

- **Razón**: es la línea base estándar en la literatura de recompra y *churn*. Permite medir cuánto aportan los modelos no lineales y sus coeficientes son interpretables.
- **Configuración prevista**: regularización L2 (se ajusta `C`), `class_weight='balanced'` para el desbalance, variables numéricas transformadas con `log1p` y estandarizadas (necesario por el sesgo observado en el EDA), variables categóricas (edad, género) codificadas *one-hot*.

### 4.2 Random Forest — ensamble por *bagging*

- **Razón**: modelo no lineal robusto a los outliers y a las distribuciones sesgadas documentadas en el EDA, sin necesidad de transformar variables. Es consistentemente competitivo en la literatura de *churn*.
- **Configuración prevista**: se ajustan `n_estimators`, `max_depth`, `min_samples_leaf` y `max_features`; `class_weight='balanced_subsample'`.

### 4.3 LightGBM — ensamble por *boosting* (modelo principal candidato)

- **Razón**: el *gradient boosting* obtuvo el mejor rendimiento individual en la solución ganadora de este mismo reto (Liu et al., 2016) y LightGBM es la implementación más eficiente para el volumen de datos disponible (Ke et al., 2017).
- **Configuración prevista**: se ajustan `num_leaves`, `learning_rate`, `n_estimators`, `min_child_samples`, `subsample`, `colsample_bytree` y regularización `reg_lambda`; `scale_pos_weight` o `is_unbalance` para el desbalance.
- **Alternativa**: si LightGBM no se puede instalar en el entorno, se usará XGBoost o `HistGradientBoostingClassifier` de scikit-learn, que implementa el mismo principio basado en histogramas.

> **Nota de implementación**: la configuración final de cada modelo, incluidos los espacios de búsqueda realmente usados, está en `09_modelado_resultados.md`. `n_estimators` se ajustó como hiperparámetro (sin parada temprana), no se usaron Optuna ni SHAP y se implementó el ensamble (sección 4.4), pero no XGBoost.

### 4.4 Opcional: XGBoost y ensamble por promedio

- Si el tiempo lo permite, se entrenará **XGBoost** como cuarto modelo para comparar dos implementaciones de *boosting*, y un **ensamble por promedio de probabilidades** de los mejores modelos, siguiendo la estrategia de Liu et al. (2016).

### 4.5 Algoritmos descartados

- **SVM**: su costo computacional crece de forma superlineal con el número de observaciones (~260,000) y no mostró ventajas claras en la literatura revisada.
- **Redes neuronales profundas**: no ofrecen ventajas claras sobre el *boosting* en datos tabulares de este tamaño y requieren más ajuste y cómputo.
- **SMOTE**: se descarta como técnica principal. Con ~245,000 observaciones negativas, generar ejemplos sintéticos es costoso y los modelos seleccionados permiten tratar el desbalance mediante ponderación de clases, enfoque recomendado por He y Garcia (2009). Puede evaluarse como experimento secundario.

---

## 5. Métricas de evaluación seleccionadas

| Métrica | Rol | Justificación |
|---|---|---|
| **AUC-ROC** | Métrica principal | Métrica oficial de la competencia; mide la capacidad de ordenar a los clientes por probabilidad de recompra, independiente del umbral (Fawcett, 2006). |
| **AUC-PR** (*average precision*) | Métrica secundaria | Más informativa que ROC con clases desbalanceadas (Saito y Rehmsmeier, 2015). Línea base aleatoria = 0.061. |
| **Recall, precisión y F1 de la clase positiva** | Métricas con umbral | Describen el comportamiento en el umbral de decisión elegido. |
| **Matriz de confusión** | Diagnóstico | Muestra los tipos de error en el umbral elegido. |
| **Tiempo de entrenamiento y de predicción** | Eficiencia | Requerido por la guía para comparar algoritmos. |

La **exactitud (*accuracy*) no se utiliza como métrica de selección**: un modelo que predijera siempre "no recurrente" obtendría 93.9 % de exactitud sin ningún valor predictivo (He y Garcia, 2009).

---

## 6. Referencias (formato APA 7)

| # | Referencia | Tipo | Verificada |
|---|---|---|---|
| 1 | Akiba, T., Sano, S., Yanase, T., Ohta, T., & Koyama, M. (2019). Optuna: A next-generation hyperparameter optimization framework. En *Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining* (pp. 2623–2631). ACM. https://doi.org/10.1145/3292500.3330701 | Conferencia (ACM) | ☐ |
| 2 | Bergstra, J., & Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research, 13*, 281–305. | Revista | ☐ |
| 3 | Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. https://doi.org/10.1023/A:1010933404324 | Revista | ☐ |
| 4 | Buckinx, W., & Van den Poel, D. (2005). Customer base analysis: Partial defection of behaviourally loyal clients in a non-contractual FMCG retail setting. *European Journal of Operational Research, 164*(1), 252–268. https://doi.org/10.1016/j.ejor.2003.12.010 | Revista | ☐ |
| 5 | Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. *Journal of Artificial Intelligence Research, 16*, 321–357. https://doi.org/10.1613/jair.953 | Revista | ☐ |
| 6 | Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. En *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785–794). ACM. https://doi.org/10.1145/2939672.2939785 | Conferencia (ACM) | ☐ |
| 7 | Coussement, K., & Van den Poel, D. (2008). Churn prediction in subscription services: An application of support vector machines while comparing two parameter-selection techniques. *Expert Systems with Applications, 34*(1), 313–327. https://doi.org/10.1016/j.eswa.2006.09.038 | Revista | ☐ |
| 8 | Fawcett, T. (2006). An introduction to ROC analysis. *Pattern Recognition Letters, 27*(8), 861–874. https://doi.org/10.1016/j.patrec.2005.10.010 | Revista | ☐ |
| 9 | Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics, 29*(5), 1189–1232. https://doi.org/10.1214/aos/1013203451 | Revista | ☐ |
| 10 | He, H., & Garcia, E. A. (2009). Learning from imbalanced data. *IEEE Transactions on Knowledge and Data Engineering, 21*(9), 1263–1284. https://doi.org/10.1109/TKDE.2008.239 | Revista (IEEE) | ☐ |
| 11 | Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. En *Advances in Neural Information Processing Systems 30* (pp. 3146–3154). Curran Associates. | Conferencia (NeurIPS) | ☐ |
| 12 | Kohavi, R. (1995). A study of cross-validation and bootstrap for accuracy estimation and model selection. En *Proceedings of the 14th International Joint Conference on Artificial Intelligence* (Vol. 2, pp. 1137–1145). Morgan Kaufmann. | Conferencia (IJCAI) | ☐ |
| 13 | Lemmens, A., & Croux, C. (2006). Bagging and boosting classification trees to predict churn. *Journal of Marketing Research, 43*(2), 276–286. https://doi.org/10.1509/jmkr.43.2.276 | Revista | ☐ |
| 14 | Liu, G., Nguyen, T. T., Zhao, G., Zha, W., Yang, J., Cao, J., Wu, M., Zhao, P., & Chen, W. (2016). Repeat buyer prediction for e-commerce. En *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 155–164). ACM. https://doi.org/10.1145/2939672.2939674 | Conferencia (ACM) | ☐ |
| 15 | Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. En *Advances in Neural Information Processing Systems 30* (pp. 4765–4774). Curran Associates. | Conferencia (NeurIPS) | ☐ |
| 16 | Neslin, S. A., Gupta, S., Kamakura, W., Lu, J., & Mason, C. H. (2006). Defection detection: Measuring and understanding the predictive accuracy of customer churn models. *Journal of Marketing Research, 43*(2), 204–211. https://doi.org/10.1509/jmkr.43.2.204 | Revista | ☐ |
| 17 | Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830. | Revista | ☐ |
| 18 | Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLoS ONE, 10*(3), e0118432. https://doi.org/10.1371/journal.pone.0118432 | Revista | ☐ |
| 19 | Verbeke, W., Dejaeger, K., Martens, D., Hur, J., & Baesens, B. (2012). New insights into churn prediction in the telecommunication sector: A profit driven data mining approach. *European Journal of Operational Research, 218*(1), 211–229. https://doi.org/10.1016/j.ejor.2011.09.031 | Revista | ☐ |

Referencias del EDA que se mantienen para el marco teórico (ver `01_contexto_investigacion.md`): Gupta y Zeithaml (2006), Fader, Hardie y Lee (2005) y Berman (2006).
