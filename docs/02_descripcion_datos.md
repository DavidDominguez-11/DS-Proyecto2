# Descripción de los Datos

## 1. Origen de los Datos

Los datos provienen de la competencia **"Repeat Buyers Prediction"** organizada por Alibaba en la plataforma [Tianchi](https://tianchi.aliyun.com/competition/entrance/231576/information). Contienen registros anonimizados de la plataforma de comercio electrónico Tmall, cubriendo un periodo que incluye el festival de compras Double 11 (11 de noviembre). El formato utilizado es `data_format1`.

## 2. Archivos Disponibles

El conjunto de datos consta de cinco archivos CSV ubicados en el directorio `data/`:

| Archivo | Ubicación | Tamaño | Filas | Columnas |
|---------|-----------|--------|-------|----------|
| `train_format1.csv` | `data/data_format1/` | 3.4 MB | 260,864 | 3 |
| `test_format1.csv` | `data/data_format1/` | 3.1 MB | 261,477 | 3 |
| `user_info_format1.csv` | `data/data_format1/` | 4.3 MB | 424,170 | 3 |
| `user_log_format1.csv` | `data/data_format1/` | 1.9 GB | 54,925,330 | 7 |
| `sample_submission.csv` | `data/` | 3.9 MB | 261,477 | 3 |

---

## 3. Descripción Detallada por Archivo

### 3.1 `train_format1.csv` — Conjunto de Entrenamiento

- **Propósito**: Define los pares usuario-vendedor que se deben analizar, junto con la etiqueta que indica si el usuario fue un comprador recurrente para ese vendedor.
- **Granularidad**: Un registro por cada par único (user_id, merchant_id).
- **Filas**: 260,864
- **Columnas**: 3
- **Valores faltantes**: Ninguno.
- **Duplicados**: Ninguno.

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `user_id` | int64 | Identificador único anonimizado del usuario. |
| `merchant_id` | int64 | Identificador único anonimizado del vendedor (comerciante). |
| `label` | int64 | Variable objetivo: 1 = comprador recurrente, 0 = no recurrente. |

**Distribución de la variable objetivo**:
- `label = 0` (no recurrente): 244,912 registros (93.9%)
- `label = 1` (recurrente): 15,952 registros (6.1%)

> **Observación**: Existe un desbalance significativo en la variable objetivo. Solo el 6.1% de los pares usuario-vendedor corresponden a compradores recurrentes. Esto debe considerarse en cualquier análisis posterior.

---

### 3.2 `test_format1.csv` — Conjunto de Prueba

- **Propósito**: Define los pares usuario-vendedor para los que se debería predecir la probabilidad de recompra (en un contexto de modelado, no en este proyecto EDA).
- **Granularidad**: Un registro por cada par único (user_id, merchant_id).
- **Filas**: 261,477
- **Columnas**: 3
- **Valores faltantes**: La columna `prob` está completamente vacía (261,477 NaN).
- **Duplicados**: Ninguno.

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `user_id` | int64 | Identificador único del usuario. |
| `merchant_id` | int64 | Identificador único del vendedor. |
| `prob` | float64 | Probabilidad de recompra (vacío, a predecir). |

> **Observación**: Este archivo no se utiliza directamente en el EDA, pero su estructura permite verificar la consistencia de los datos.

---

### 3.3 `user_info_format1.csv` — Perfil de Usuarios

- **Propósito**: Proporciona información demográfica básica de los usuarios.
- **Granularidad**: Un registro por usuario.
- **Filas**: 424,170
- **Columnas**: 3
- **Valores faltantes**: age_range: 2,217 NaN; gender: 6,436 NaN.
- **Duplicados**: Ninguno.

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `user_id` | int64 | Identificador único del usuario. |
| `age_range` | float64 | Rango de edad codificado (ver tabla de codificación abajo). |
| `gender` | float64 | Género codificado (ver tabla de codificación abajo). |

**Codificación de `age_range`**:

| Código | Significado |
|--------|-------------|
| 0 | Desconocido |
| 1 | Menor de 18 años |
| 2 | 18–24 años |
| 3 | 25–29 años |
| 4 | 30–34 años |
| 5 | 35–39 años |
| 6 | 40–49 años |
| 7 | 50 años o más |
| 8 | 50 años o más |
| NaN | No reportado |

**Codificación de `gender`**:

| Código | Significado |
|--------|-------------|
| 0 | Femenino |
| 1 | Masculino |
| 2 | Desconocido |
| NaN | No reportado |

> **Observación**: Los valores 0 en `age_range` representan desconocido, los códigos 7 y 8 corresponden a `50+` y los NaN representan valores faltantes reales. En `gender`, el código 2 sí representa desconocido y los NaN representan ausencia real de dato. El archivo contiene más usuarios (424,170) que los presentes en el conjunto de entrenamiento (260,864 pares, con menos usuarios únicos), lo que indica que incluye usuarios del conjunto de prueba y posiblemente otros.

---

### 3.4 `user_log_format1.csv` — Registro de Actividad

- **Propósito**: Contiene el historial de interacciones de los usuarios con productos en la plataforma Tmall.
- **Granularidad**: Un registro por cada interacción individual (clic, adición al carrito, compra o favorito).
- **Filas**: 54,925,330 (~55 millones)
- **Columnas**: 7
- **Valores faltantes**: `brand_id`: 91,015 NaN (0.17% del total).
- **Duplicados**: No verificados de forma exhaustiva debido al tamaño del archivo.

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `user_id` | int64 | Identificador único del usuario. |
| `item_id` | int64 | Identificador único del producto. |
| `cat_id` | int64 | Identificador de la categoría del producto. |
| `seller_id` | int64 | Identificador del vendedor. **Corresponde a `merchant_id`** en train/test. |
| `brand_id` | float64* | Identificador de la marca del producto. Contiene 91,015 valores nulos. |
| `time_stamp` | int64 | Marca temporal en formato MMDD (ejemplo: 511 = 11 de mayo, 1111 = 11 de noviembre). |
| `action_type` | int64 | Tipo de acción realizada (ver tabla de codificación abajo). |

*\* `brand_id` se carga como float64 debido a la presencia de valores NaN.*

**Codificación de `action_type`**:

| Código | Significado |
|--------|-------------|
| 0 | Clic (visualización del producto) |
| 1 | Adición al carrito de compras |
| 2 | Compra |
| 3 | Adición a favoritos |

**Rango de `time_stamp`**: 511 (11 de mayo) a 1112 (12 de noviembre).

> **Observación**: El periodo cubierto abarca aproximadamente 6 meses, desde mayo hasta noviembre, incluyendo el festival Double 11. La columna `seller_id` en este archivo corresponde a `merchant_id` en los archivos de entrenamiento y prueba. Este archivo es el más grande del conjunto de datos y requiere procesamiento por fragmentos (*chunks*) para evitar problemas de memoria.

---

### 3.5 `sample_submission.csv` — Formato de Envío

- **Propósito**: Proporciona el formato esperado para una predicción en el contexto de la competencia. No se utiliza en el EDA.
- **Filas**: 261,477
- **Columnas**: 3 (user_id, merchant_id, prob)

---

## 4. Relaciones entre Archivos

```
┌─────────────────┐     user_id      ┌──────────────────┐
│  train / test    │◄────────────────►│   user_info      │
│  (user_id,       │                  │   (user_id,      │
│   merchant_id,   │                  │    age_range,     │
│   label/prob)    │                  │    gender)        │
└────────┬────────┘                  └──────────────────┘
         │
         │ user_id + merchant_id = user_id + seller_id
         │
         ▼
┌─────────────────────────────────────────┐
│              user_log                    │
│  (user_id, item_id, cat_id, seller_id,  │
│   brand_id, time_stamp, action_type)     │
└─────────────────────────────────────────┘
```

- **train/test → user_info**: Se relacionan por `user_id`. No todos los usuarios de train/test necesariamente tienen perfil en user_info.
- **train/test → user_log**: Se relacionan por `user_id` y `merchant_id` (en train/test) = `seller_id` (en user_log). Un par usuario-vendedor en train/test puede tener múltiples registros de actividad en user_log.
- **user_log**: Contiene la actividad detallada que permite construir métricas agregadas por par (user_id, seller_id) para enriquecer el análisis de los pares del conjunto de entrenamiento.

## 5. Observaciones Generales

1. **Desbalance de clases**: Solo el 6.1% de los pares en entrenamiento son compradores recurrentes, lo que representa un desbalance severo.
2. **Datos demográficos incompletos**: Una proporción significativa de usuarios tiene valores desconocidos o faltantes en edad y género, lo que limita el análisis demográfico.
3. **Volumen de datos de actividad**: Con casi 55 millones de registros, el archivo de logs requiere estrategias eficientes de procesamiento.
4. **Relación seller_id ↔ merchant_id**: Es fundamental mapear correctamente `seller_id` del log a `merchant_id` del entrenamiento.
5. **Marca temporal**: El formato MMDD requiere interpretación cuidadosa; no es un timestamp estándar.