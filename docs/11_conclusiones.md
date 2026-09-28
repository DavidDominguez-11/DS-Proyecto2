# Conclusiones

Este documento reúne el cumplimiento de los objetivos, la discusión de la efectividad de los algoritmos, recomendaciones, limitaciones y trabajo futuro. Se evalúan los objetivos del análisis exploratorio (`01_contexto_investigacion.md`) y los de la fase de modelado (`07_metodologia_modelado.md`).

---

## 1. Cumplimiento de los objetivos

**Objetivos del análisis exploratorio (`01_contexto_investigacion.md`) — Caracterizar los datos. Cumplidos.**
- **Desbalance severo**: solo el 6.12 % de los 260,864 compradores nuevos volvió a comprar.
- **Concentración en el Double 11**: el 11 de noviembre reúne el 37.2 % de todas las compras del periodo.
- **Diferencias de comportamiento**: los compradores recurrentes interactúan más con el vendedor (media de 17.1 frente a 10.4 acciones), exploran más productos (7.5 frente a 4.2) y están activos más días.
- **Señal débil y repartida**: las diferencias son pequeñas y ninguna variable, por sí sola, se correlaciona fuertemente con la recompra (|r| ≤ 0.10; tamaño del efecto de Mann-Whitney ≤ 0.20).
- **Demografía poco informativa**: la edad y el género se asocian con la recompra de forma muy débil (V de Cramér ≈ 0.02).
- **Conclusión para el modelado**: estos hallazgos anticiparon que haría falta combinar muchas variables en modelos no lineales.

**Objetivo específico 1 de modelado — Construir variables en varios niveles sin fuga. Cumplido.**
- **Variables construidas**: 64, a partir de 55 millones de interacciones: 24 del par, 19 del usuario, 16 del vendedor, 3 de relación y 2 demográficas.
- **Verificación de la definición**: todos los pares compraron por primera vez al vendedor el 11/11.
- **Sin fuga**: se verificó que no hay fuga desde el día posterior al evento. La tasa de recompra del vendedor se calculó con ajuste cruzado dentro del `Pipeline`; el encoding con fuga habría inflado el AUC de entrenamiento de 0.651 a 0.705.
- **Mejor variable individual**: la fidelidad histórica de la clientela del vendedor, calculada sin la etiqueta (AUC 0.622).

**Objetivo específico 2 de modelado — Entrenar y ajustar al menos tres algoritmos. Cumplido.**
- **Modelos y búsqueda**: se ajustaron Regresión Logística, Random Forest y LightGBM con búsqueda aleatoria sobre 5 pliegues agrupados por usuario, y se agregó un ensamble.
- **Efecto del ajuste**: mejoró sobre todo a Random Forest (+0.041 de AUC), que con su configuración por defecto memorizaba el entrenamiento, y en menor medida a LightGBM (+0.007).

**Objetivo específico 3 de modelado — Evaluar, comparar y seleccionar. Cumplido, con un matiz.**
- **Meta de AUC**: se alcanzó con holgura. Todos los modelos obtuvieron un AUC-ROC de 0.686–0.691 en un conjunto de prueba con usuarios que nunca vieron, frente a la meta de 0.65, al azar (0.5) y a la mejor variable individual (0.614).
- **Selección**: se eligió **LightGBM**, con el mejor AUC de validación cruzada (0.693), la menor variabilidad entre pliegues y el mejor AUC-PR en prueba (0.139).
- **El matiz: superar a la Regresión Logística base se cumplió solo de forma marginal.** LightGBM la supera por 0.0016 de AUC en validación cruzada y por 0.002 de AUC-PR, pero empatan en AUC-ROC de prueba (0.689). Una regresión logística bien preprocesada (`log1p`, estandarización, *target encoding*) captura casi toda la señal disponible, y los modelos más complejos no encuentran relaciones adicionales relevantes.

**Objetivo específico 4 de modelado — Desarrollar una aplicación interactiva. Cumplido.**
- **Qué permite**: explorar las 64 variables, comparar el rendimiento de uno o todos los modelos con gráficas interactivas que se pueden ocultar, y clasificar compradores de tres formas (búsqueda, formulario manual o archivo).
- **Preprocesamiento**: es transparente para el usuario.
- **Predicciones**: coinciden exactamente con las del notebook de modelado.

**Objetivo general. Cumplido.** Se desarrollaron, ajustaron y compararon modelos que estiman la probabilidad de recompra de los compradores nuevos del Double 11, a partir de un análisis exploratorio, y se integraron en una aplicación interactiva.

## 2. Efectividad de los algoritmos

- **Los cuatro modelos rinden prácticamente igual.** Las diferencias de AUC (≤ 0.005) son del mismo orden que la variabilidad entre pliegues de validación cruzada, y sus curvas ROC, precisión-recall y de ganancia casi se superponen. El límite lo impone la información disponible en los datos, no el algoritmo. Esto concuerda con la observación de Liu et al. (2016) de que en este problema la ingeniería de variables pesa más que la elección del modelo, y el AUC obtenido es cercano al ~0.70 reportado para la solución ganadora de la competencia.
- **Los modelos son útiles en la práctica, aunque no clasifican de forma precisa a cada comprador.**
  - Contactando solo al 10 % de los compradores con mayor puntaje se alcanza al ~27 % de los que realmente volverán, 2.7 veces más que eligiendo al azar.
  - Con el umbral que maximiza F1, de cada 100 compradores señalados como recurrentes unos 15 lo son, frente a 6 al azar.
  - Aun así, F1 es de ~0.21 y la mayoría de los señalados no vuelve. Por eso el modelo es adecuado para **priorizar** acciones de retención de bajo costo (cupones, mensajes, recomendaciones), no para decisiones costosas sobre individuos.
- **Comparación de costo y beneficio entre algoritmos**:
  - **LightGBM** ofrece el mejor equilibrio entre rendimiento, estabilidad y tiempo (se entrena en ~5 s).
  - **Regresión Logística**: es la opción más rápida e interpretable, con rendimiento prácticamente igual.
  - **Random Forest**: es el más costoso de ajustar y almacenar, sin ventaja de rendimiento.
  - **Ensamble**: mejora el AUC en solo 0.001, lo que no justifica mantener tres modelos.
- **Hallazgo principal: lo que más predice la recompra es el vendedor.** Su tasa histórica de recompra concentra ~20 % de la importancia en los modelos de árboles. Le siguen la profundidad y la antigüedad de la relación del comprador con el vendedor (productos y categorías explorados, compras, actividad previa al Double 11). Los hábitos generales del usuario aportan información complementaria, y la demografía casi no aporta.

## 3. Recomendaciones

1. **Priorizar la retención con el puntaje del modelo.** Concentrar cupones o mensajes posteriores al Double 11 en el decil superior de puntaje: allí vuelve a comprar el 16.6 % de los compradores (LightGBM), 2.7 veces la tasa base.
2. **Diferenciar la estrategia por vendedor.** La fidelidad histórica de la clientela del vendedor es el factor más predictivo; los vendedores con clientela poco fiel necesitan incentivos adicionales para retener a los compradores de la promoción.
3. **Fomentar la exploración y la relación antes del evento.** Los compradores que ya visitaban al vendedor y exploraron más productos vuelven más, lo que sugiere invertir en atraer visitas y favoritos antes del Double 11, no solo en descuentos el mismo día.
4. **No basar la segmentación en la demografía**, que aporta muy poca información sobre la recompra.

## 4. Limitaciones

- **Desbalance severo** (6.1 % de positivos): limita la precisión alcanzable en la clase de interés.
- **Sin montos de compra**: no se puede usar el componente monetario del análisis RFM ni estimar el valor del cliente.
- **Granularidad temporal limitada**: `time_stamp` no tiene año ni hora.
- **Filas repetidas en el registro**: el 25 % de las filas son repeticiones exactas y no se pueden distinguir de duplicados por error.
- **Demografía incompleta**: la edad es desconocida en el 21.9 % de los pares.
- **Generalización**: los datos provienen de una sola plataforma y de un solo periodo con el Double 11.
- **Evaluación interna**: el conjunto de prueba oficial no tiene etiquetas, así que la evaluación se basa en una partición interna (agrupada por usuario para imitar la estructura oficial). Además, una prueba rápida inicial del código imprimió métricas del conjunto de prueba, aunque las decisiones se tomaron solo con validación cruzada.
- **Puntajes no calibrados**: los puntajes de los modelos con pesos de clase balanceados no son probabilidades calibradas; por eso la aplicación presenta percentiles y tasas observadas por decil.
- **Búsqueda de hiperparámetros**: fue limitada (12 a 30 configuraciones por modelo), y el mejor valor de `C` de la regresión logística quedó cerca del límite del rango explorado.

## 5. Trabajo futuro

- **Más ingeniería de variables**: variables a nivel de categoría y marca, similitud entre el usuario y la oferta del vendedor, ventanas temporales (última semana o último mes antes del evento) y secuencias de acciones, que es donde la literatura encontró las mayores ganancias.
- **Calibrar las probabilidades** (Platt o isotónica) y **elegir el umbral según el costo** de una acción de retención frente al valor de un cliente recurrente.
- **Explicaciones individuales con SHAP** (Lundberg & Lee, 2017) en la aplicación.
- **Probar XGBoost y ensambles apilados** (*stacking*), y ampliar la búsqueda de hiperparámetros con optimización bayesiana (Akiba et al., 2019).
- **Validar con datos de otro periodo promocional** para medir la estabilidad del modelo en el tiempo.
