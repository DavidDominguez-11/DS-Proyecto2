# Limpieza y Preprocesamiento

Este documento describe las revisiones de calidad de datos, las decisiones de limpieza y las transformaciones aplicadas durante el análisis exploratorio. Se distingue claramente entre los datos originales, las operaciones de limpieza y las variables derivadas construidas para el análisis.

---

## 1. Estado de los Datos Originales

### 1.1 Resumen de calidad por archivo

| Archivo | Filas | Duplicados | Valores Faltantes | Observaciones |
|---------|-------|------------|-------------------|---------------|
| `train_format1.csv` | 260,864 | 0 | Ninguno | Datos limpios. |
| `test_format1.csv` | 261,477 | 0 | `prob`: 261,477 (por diseño) | Columna `prob` vacía es esperada. |
| `user_info_format1.csv` | 424,170 | 0 | `age_range`: 2,217; `gender`: 6,436 | Valores NaN reales + códigos de "desconocido". |
| `user_log_format1.csv` | 54,925,330 | No verificado exhaustivamente | `brand_id`: 91,015 | Archivo demasiado grande para verificación completa de duplicados. |

---

## 2. Revisiones de Calidad Realizadas

### 2.1 Duplicados

- **train_format1.csv**: No se encontraron filas duplicadas. Cada par (user_id, merchant_id) es único.
- **test_format1.csv**: No se encontraron filas duplicadas.
- **user_info_format1.csv**: No se encontraron user_id duplicados.
- **user_log_format1.csv**: No se realizó una verificación exhaustiva de duplicados debido al tamaño del archivo (55 millones de filas). Es posible que existan registros con el mismo (user_id, item_id, seller_id, time_stamp, action_type), ya que un usuario podría hacer clic en el mismo producto múltiples veces en el mismo día. Estos registros se conservan porque representan interacciones repetidas legítimas.

### 2.2 Valores Faltantes

#### En `user_info_format1.csv`
- **`age_range`**: 2,217 valores NaN (0.52% de los usuarios).
- **`gender`**: 6,436 valores NaN (1.52% de los usuarios).
- **Decisión**: Los valores NaN en `age_range` se recodifican como 0 (desconocido) y los códigos 7 y 8 se consolidan en una sola categoría analítica `50+`. Los NaN en `gender` se recodifican como 2 (desconocido), unificándolos con las categorías "desconocido" ya existentes en la codificación original. Esto permite incluir a todos los usuarios en el análisis sin eliminar registros ni fragmentar el grupo mayor de edad.
- **Justificación**: Eliminar usuarios sin datos demográficos excluiría sus interacciones del análisis, reduciendo la muestra sin justificación analítica. Al consolidarlos en la categoría "desconocido", se preserva la información de actividad y se documenta la limitación.

#### En `user_log_format1.csv`
- **`brand_id`**: 91,015 valores NaN (0.17% de los registros de actividad).
- **Decisión**: Se conservan los registros sin marca. Para métricas que requieren contar marcas únicas, los NaN se excluyen del conteo de diversidad pero el registro se mantiene en el cálculo de otras métricas (acciones totales, clics, etc.).
- **Justificación**: La ausencia de marca no invalida la interacción del usuario con el producto. Eliminar estos registros afectaría las métricas de actividad total sin un beneficio analítico claro.

### 2.3 Códigos especiales de recodificación

Además de los valores NaN, los datos contienen categorías explícitas que requieren tratamiento especial:

| Variable | Código | Significado | Cantidad (aprox.) |
|----------|--------|-------------|-------------------|
| `age_range` | 0 | Desconocido | Variable (ver notebook) |
| `age_range` | 8 | 50 años o más | Variable (ver notebook) |
| `gender` | 2 | Desconocido | Variable (ver notebook) |

**Decisión**: `age_range = 0` y el `NaN` original se consideran desconocidos; `age_range = 7` y `age_range = 8` se consolidan en la categoría analítica `50+`; `gender = 2` y el `NaN` original se consideran desconocidos. Estas categorías se reportan por separado en los gráficos y tablas de frecuencia para que el lector pueda evaluar su impacto. No se eliminan ni se imputan valores para estas categorías, ya que la imputación introduciría supuestos no justificados.

### 2.4 Validación de Llaves

- **user_id en train → user_info**: Se verificó cuántos usuarios del conjunto de entrenamiento tienen perfil demográfico disponible en user_info. No todos los usuarios de train necesariamente existen en user_info. Los pares sin información demográfica reciben valores de "desconocido" en el merge.
- **merchant_id en train → seller_id en user_log**: Se verificó la correspondencia entre `merchant_id` del entrenamiento y `seller_id` del log de actividad. Algunos pares (user_id, merchant_id) del entrenamiento podrían no tener actividad registrada en user_log; estos se conservan con métricas de actividad en cero o NaN, documentando la ausencia.
- **Consistencia train ↔ test**: Se verificó que los conjuntos de entrenamiento y prueba no comparten los mismos pares (user_id, merchant_id), confirmando la separación adecuada.

### 2.5 Validación de Valores Esperados

- **`label`**: Se verificó que solo contiene valores 0 y 1, sin valores inesperados.
- **`action_type`**: Se verificó que solo contiene valores 0, 1, 2 y 3, consistente con la documentación.
- **`time_stamp`**: Rango observado de 511 a 1112 (formato MMDD). Se verificó que los valores sean plausibles como fechas (mayo a noviembre).

### 2.6 Marca Temporal (time_stamp)

- **Formato**: Entero en formato MMDD (ejemplo: 511 = 11 de mayo, 1111 = 11 de noviembre, 1112 = 12 de noviembre).
- **Tratamiento**: Se utiliza como identificador de fecha para contar días activos por par usuario-vendedor. No se convierte a formato datetime estándar ya que el entero MMDD es suficiente para las métricas de conteo y no se dispone del año para una conversión completa.
- **Observación**: El rango cubre aproximadamente 6 meses (mayo a noviembre), incluyendo el periodo del festival Double 11.

### 2.7 Tipos de Datos

- Los identificadores (`user_id`, `merchant_id`, `seller_id`, `item_id`, `cat_id`, `brand_id`) se tratan como identificadores categóricos, no como variables numéricas. No se incluyen en análisis de correlación ni en estadísticas descriptivas numéricas.
- `age_range` y `gender` se tratan como variables categóricas ordinales/nominales, no como valores numéricos continuos. Para el análisis, `age_range = 7` y `age_range = 8` se consolidan en `50+`.
- `label` y `action_type` se tratan como variables categóricas binarias/nominales.

---

## 3. Operaciones de Limpieza Aplicadas

### 3.1 Datos preservados sin modificación (DataFrames crudos)
- `train_raw`: Copia intacta de `train_format1.csv`.
- `test_raw`: Copia intacta de `test_format1.csv`.
- `user_info_raw`: Copia intacta de `user_info_format1.csv`.

### 3.2 Copias limpias creadas
- **`user_info_clean`**: Copia de `user_info_raw` con las siguientes modificaciones:
  - `age_range`: NaN → 0 (categoría "desconocido").
  - `age_range`: 7 y 8 → `50+` en la representación analítica.
  - `gender`: NaN → 2 (categoría "desconocido").
  - Conversión de `age_range` y `gender` a tipo `int64` después de la imputación.

- **`train_clean`**: Igual a `train_raw` (no requirió limpieza).

---

## 4. Variables Derivadas para Análisis

Las siguientes métricas se construyeron a partir de `user_log_format1.csv`, agregando por par (user_id, seller_id):

| Variable Derivada | Descripción | Cálculo |
|-------------------|-------------|---------|
| `total_actions` | Total de interacciones del par usuario-vendedor | Conteo de registros por (user_id, seller_id) |
| `clicks` | Cantidad de clics (visualizaciones) | Conteo de registros con action_type = 0 |
| `cart` | Cantidad de adiciones al carrito | Conteo de registros con action_type = 1 |
| `purchase` | Cantidad de compras | Conteo de registros con action_type = 2 |
| `favorite` | Cantidad de adiciones a favoritos | Conteo de registros con action_type = 3 |
| `n_items` | Productos únicos explorados | Conteo exacto de `item_id` distintos por (user_id, seller_id) |
| `n_cats` | Categorías únicas exploradas | Conteo exacto de `cat_id` distintos por (user_id, seller_id) |
| `n_brands` | Marcas únicas exploradas | Conteo exacto de `brand_id` distintos (excluyendo NaN) por (user_id, seller_id) |
| `n_days` | Días con actividad | Conteo exacto de `time_stamp` distintos por (user_id, seller_id) |
| `click_rate` | Proporción de clics sobre el total | clicks / total_actions |
| `purchase_rate` | Proporción de compras sobre el total | purchase / total_actions |
| `cart_rate` | Proporción de adiciones al carrito sobre el total | cart / total_actions |
| `favorite_rate` | Proporción de adiciones a favoritos sobre el total | favorite / total_actions |

**Nota sobre fuga de información**: Todas las métricas derivadas provienen exclusivamente de los registros de actividad del usuario con el vendedor (user_log). No se utilizó la etiqueta (`label`) para construir estas variables.

---

## 5. Construcción de la Tabla Analítica

La tabla analítica final se construyó mediante los siguientes pasos:

1. **Base**: Conjunto de entrenamiento `train_clean` (260,864 filas, unidad: par user_id-merchant_id).
2. **Merge con user_info_clean**: Left join por `user_id`, agregando `age_range` y `gender`.
3. **Merge con métricas de actividad**: Left join por (`user_id`, `merchant_id` = `seller_id`), agregando todas las variables derivadas.
4. **Tratamiento de pares sin actividad**: Los pares usuario-vendedor sin registros en user_log reciben 0 en conteos y NaN en tasas (que se reemplazan por 0).
5. **Resultado**: Una tabla con 260,864 filas y columnas que incluyen la etiqueta, datos demográficos y métricas de actividad.

---

## 6. Limitaciones de Calidad de Datos

1. **Valores demográficos desconocidos**: Una proporción sustancial de usuarios tiene edad y/o género desconocidos, lo que limita las conclusiones demográficas.
2. **Particionado de user_log**: El archivo se divide en particiones en disco mediante un hash determinista del par `(user_id, seller_id)`. Por ello, todos los registros de un mismo par quedan en una misma partición, lo que permite calcular de forma global y exacta los conteos distintos de `n_items`, `n_cats`, `n_brands` y `n_days`.
3. **Marca temporal imprecisa**: El formato MMDD no incluye año ni hora, limitando el análisis temporal a la granularidad de días.
4. **Sesgo de muestreo posible**: Los datos provienen de una plataforma específica (Tmall) durante un periodo específico, por lo que los patrones encontrados podrían no generalizarse a otros contextos.
5. **brand_id faltantes**: 91,015 registros sin marca podrían subestimar la diversidad de marcas en las métricas derivadas.
6. **Pares sin actividad**: Algunos pares del entrenamiento podrían no tener actividad registrada en user_log, lo que limita el análisis de comportamiento para esos casos.
