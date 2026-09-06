# Contexto e Investigación

## 1. Situación Problemática

Las plataformas de comercio electrónico invierten recursos significativos en la adquisición de nuevos clientes, particularmente durante eventos promocionales masivos como el **Double 11** (11 de noviembre), el mayor festival de compras en línea del mundo, organizado por Alibaba a través de su plataforma Tmall. Durante estos eventos, los comerciantes ofrecen descuentos agresivos para atraer nuevos compradores; sin embargo, una proporción considerable de estos clientes adquiridos durante promociones resultan ser compradores únicos que no regresan.

Esta situación genera un problema económico importante: el costo de adquisición de clientes que no retornan supera con creces el margen de ganancia obtenido de sus compras puntuales. Para los comerciantes, distinguir entre compradores que volverán a comprar y aquellos que solo responden a descuentos temporales es esencial para diseñar estrategias de retención eficientes y asignar presupuestos de marketing de manera informada.

El presente proyecto se centra en analizar los datos disponibles de la competencia **"Repeat Buyers Prediction"** de la plataforma Tianchi de Alibaba, con el fin de explorar qué patrones de comportamiento y características demográficas se asocian con la recompra recurrente a un mismo vendedor.

## 2. Problema Científico

¿Qué patrones de comportamiento de compra (clics, adiciones al carrito, compras, favoritos) y características demográficas (edad, género) se asocian con que un usuario de la plataforma Tmall vuelva a comprar a un mismo vendedor después de un periodo promocional?

Este problema se aborda desde la perspectiva del análisis exploratorio de datos, buscando identificar asociaciones, tendencias y distribuciones que caractericen a los compradores recurrentes frente a los no recurrentes, sin asumir relaciones causales.

## 3. Objetivos

### 3.1 Objetivo General

Realizar un análisis exploratorio de datos completo sobre los registros de actividad, perfiles de usuario y etiquetas de recompra de la plataforma Tmall, para identificar los patrones de comportamiento e indicadores demográficos que distinguen a los compradores recurrentes de los no recurrentes.

### 3.2 Objetivos Específicos

1. **Caracterizar la distribución de la variable objetivo (label)** y cuantificar el grado de desbalance entre compradores recurrentes y no recurrentes en el conjunto de entrenamiento, evaluando sus implicaciones para el análisis.

2. **Construir métricas de actividad por par usuario-vendedor** (total de interacciones, distribución de tipos de acción, diversidad de productos/categorías/marcas, días activos) a partir de los registros de actividad, y analizar su relación con la probabilidad de recompra.

3. **Evaluar la asociación entre variables demográficas** (rango de edad, género) y la tasa de recompra, cuantificando la proporción de compradores recurrentes por segmento demográfico.

4. **Identificar patrones de correlación entre las métricas de actividad derivadas** y detectar valores atípicos que puedan representar comportamientos inusuales, documentando las decisiones de tratamiento.

## 4. Investigación del Tema

### 4.1 Retención de Clientes en Comercio Electrónico

La retención de clientes se refiere a la capacidad de una empresa para mantener a sus clientes a lo largo del tiempo. En el comercio electrónico, la retención es un indicador clave de salud del negocio, ya que el costo de adquisición de nuevos clientes supera significativamente al costo de retener a los existentes. Estudios en marketing han demostrado que los clientes recurrentes tienden a gastar más por transacción y tienen un mayor valor de vida del cliente (*Customer Lifetime Value*, CLV) (Gupta & Zeithaml, 2006).

### 4.2 Compradores Recurrentes y Eventos Promocionales

Los eventos promocionales masivos como el Double 11 generan un fenómeno conocido como la «paradoja del comprador promocional»: los descuentos profundos atraen a clientes sensibles al precio que rara vez regresan sin un incentivo equivalente. La clave para los comerciantes es identificar qué compradores adquiridos durante promociones tienen potencial de convertirse en clientes orgánicos y recurrentes. Modelos como el BG/NBD (*Beta-Geometric/Negative Binomial Distribution*) han sido propuestos para predecir el comportamiento de recompra a partir de datos transaccionales (Fader, Hardie & Lee, 2005).

### 4.3 Segmentación de Clientes

Las técnicas de segmentación permiten agrupar a los clientes en categorías homogéneas para diseñar estrategias diferenciadas. El análisis **RFM** (Recencia, Frecuencia, Monto) es una de las técnicas más utilizadas en comercio electrónico para clasificar clientes según su comportamiento de compra. La segmentación demográfica (edad, género) y la segmentación conductual (patrones de navegación, tasas de clic, abandono de carrito) complementan el análisis RFM y permiten una comprensión más completa del perfil del comprador (Berman, 2006).

### 4.4 Ofertas Personalizadas y Lealtad

La personalización de ofertas y recomendaciones ha demostrado ser un factor significativo en la probabilidad de recompra. Las plataformas de comercio electrónico utilizan los historiales de navegación y compra para generar recomendaciones personalizadas que aumentan tanto la tasa de conversión como la lealtad del cliente. El enfoque de «siguiente mejor oferta» (*next best offer*) utiliza datos históricos de interacción para optimizar las promociones dirigidas a cada segmento de clientes.

### 4.5 Relación con el EDA

En este análisis exploratorio, se buscarán patrones consistentes con la literatura revisada:

- **Intensidad de interacción**: se espera que los compradores recurrentes presenten mayor cantidad de acciones totales, más compras y mayor diversidad de productos explorados.
- **Tipo de interacción**: las proporciones de clics, compras, adiciones al carrito y favoritos podrían diferir entre compradores recurrentes y no recurrentes.
- **Perfil demográfico**: ciertos rangos de edad o géneros podrían presentar tasas de recompra diferentes, lo que tendría implicaciones para la segmentación.
- **Temporalidad**: la distribución de actividad a lo largo del tiempo (mayo a noviembre) podría revelar patrones estacionales asociados con la recompra.

El EDA no pretende establecer relaciones causales, sino identificar asociaciones y distribuciones que informen la selección de variables y estrategias para un futuro modelo predictivo.

## 5. Referencias

1. Gupta, S., & Zeithaml, V. (2006). Customer Metrics and Their Impact on Financial Performance. *Marketing Science*, 25(6), 718–739. Disponible en: [https://pubsonline.informs.org/doi/10.1287/mksc.1060.0221](https://pubsonline.informs.org/doi/10.1287/mksc.1060.0221)

2. Fader, P. S., Hardie, B. G. S., & Lee, K. L. (2005). Counting Your Customers the Easy Way: An Alternative to the Pareto/NBD Model. *Marketing Science*, 24(2), 275–284. Disponible en: [https://pubsonline.informs.org/doi/10.1287/mksc.1040.0098](https://pubsonline.informs.org/doi/10.1287/mksc.1040.0098)

3. Berman, B. (2006). Developing an Effective Customer Loyalty Program. *California Management Review*, 49(1), 123–148. Disponible en: [https://journals.sagepub.com/doi/10.2307/41166374](https://journals.sagepub.com/doi/10.2307/41166374)

4. Alibaba Group. 11.11 Global Shopping Festival. *Alizila*. Disponible en: [https://www.alizila.com/1111-shopping-festival/](https://www.alizila.com/1111-shopping-festival/)

5. Tianchi – Alibaba. Repeat Buyers Prediction Competition. Disponible en: [https://tianchi.aliyun.com/competition/entrance/231576/information](https://tianchi.aliyun.com/competition/entrance/231576/information)
