# Ingeniería de Variables y Partición de Datos

Este documento describe la ingeniería de variables y la partición de los datos (pasos 3 y 4 de `07_metodologia_modelado.md`). Todo se implementa en `notebooks/02_ingenieria_variables.ipynb`: la construcción de las variables de modelado a partir del registro de actividad y la partición en entrenamiento, prueba y pliegues de validación cruzada.

---

## 1. Procesamiento del registro de actividad

- Con tipos compactos (`int8`, `int16`, `int32`, `float32`), el registro completo (54,925,330 filas) ocupa **1.04 GB en memoria**, así que se carga entero. Ya no hace falta el particionado por *hash* del EDA.
- La primera ejecución convierte el CSV a **parquet** (`data/processed/user_log.parquet`), que se lee en menos de 1 segundo.
- `time_stamp` (MMDD) se convierte a **días antes del Double 11** (`dias_antes_d11`: 0 = 11/11) con un año de referencia no bisiesto. Solo importan las diferencias entre fechas.
- Los conteos de valores distintos se calculan con `drop_duplicates` sobre (grupo, valor) y un conteo por grupo. Es un cálculo exacto.
- Memoria recomendada: al menos 8 GB de RAM libres (estimación: el registro ocupa ~1 GB y las agregaciones generan copias intermedias; no se midió el pico exacto).

## 2. Verificación de la definición del problema

| Verificación | Resultado |
|---|---|
| Pares de entrenamiento cuya primera compra al vendedor fue el 11/11 | **260,864 (100 %)** |
| Pares con compras al vendedor antes del 11/11 | 0 |
| Pares con compras el 12/11 | 0 |
| Filas del 12/11 en todo el registro | 46 |

- Esto confirma la definición de "comprador nuevo del Double 11". Por ella, `p_purchase` cuenta solo compras del Double 11, y la actividad previa del par consiste únicamente en clics, carrito y favoritos.
- **No hay fuga de información desde el 12/11:** hay muy pocas filas y ninguna es una compra de un par de entrenamiento.

## 3. Variables construidas (64)

| Nivel | Cantidad | Variables principales | Idea |
|---|---:|---|---|
| **Par usuario-vendedor** (`p_`) | 24 | Las 13 del EDA, más actividad del 11/11 y previa (`p_actions_d11`, `p_actions_pre`, `p_clicks_pre`, `p_favorite_pre`, `p_cart_pre`, `p_n_days_pre`), antigüedad de la relación (`p_first_days_before`, `p_last_pre_days_before`, `p_has_pre`), `p_n_items_bought` y `p_d11_share` | Separar el interés previo al vendedor del impulso de la promoción |
| **Usuario** (`u_`) | 19 | Actividad total, vendedores/productos/categorías/marcas/días distintos, compras previas, vendedores a los que compró el 11/11, **vendedores con recompra histórica** (`u_n_merchants_repeat`, `u_repeat_share`) | Hábitos del usuario en toda la plataforma |
| **Vendedor** (`m_`) | 16 | Tamaño (usuarios, compradores, productos), conversión, dependencia del 11/11 (`m_purchase_d11_share`), **fidelidad histórica sin etiqueta** (`m_n_repeat_buyers`, `m_repeat_buyer_rate_log`) | Capacidad del vendedor de retener clientes |
| **Relación** (`x_`) | 3 | `x_share_user_actions`, `x_share_user_purchase`, `x_share_user_merchants_d11` | Cuánto pesa este vendedor en la actividad del usuario |
| **Demográficas** | 2 | `age_range` (0–7, con `50+` consolidado), `gender` (0–2) | Perfil del usuario |

El diccionario completo, con la descripción y el AUC individual de cada variable, está en `outputs/tables/diccionario_variables.csv`.

**Control de fuga:** ninguna de las 64 variables usa `label`. La "recompra histórica" (`u_n_merchants_repeat`, `m_repeat_buyer_rate_log`) se mide como compras en ≥ 2 días distintos dentro del registro, que termina el 11/11. No puede incluir la recompra que define la etiqueta, porque esta ocurre en los seis meses posteriores y el par objetivo solo tiene compras el 11/11. La tasa real de recompra del vendedor (*target encoding*) se calculará en el modelado, fuera de pliegue.

## 4. Validaciones

- **Cobertura:** no se perdieron ni duplicaron pares (260,864 de entrenamiento y 261,477 de la prueba de la competencia), no hay valores faltantes y todos los pares tienen actividad.
- **Coherencia con el EDA:** las medias de las métricas del par coinciden con las del EDA con tres decimales (por ejemplo, `p_actions` 10.826, `p_n_items` 4.381 y `p_n_days` 1.888).

## 5. Partición

Se usó `StratifiedGroupKFold` (grupos = `user_id`, estratos = `label`, semilla 42):

| Conjunto | Pares | % | Usuarios | Vendedores | Positivos | Tasa de positivos |
|---|---:|---:|---:|---:|---:|---:|
| Entrenamiento | 208,691 | 80.0 % | 169,616 | 1,991 | 12,762 | 6.12 % |
| — pliegue 0 | 41,739 | 16.0 % | 33,928 | 1,975 | 2,553 | 6.12 % |
| — pliegue 1 | 41,737 | 16.0 % | 33,888 | 1,983 | 2,552 | 6.11 % |
| — pliegue 2 | 41,738 | 16.0 % | 33,935 | 1,975 | 2,552 | 6.11 % |
| — pliegue 3 | 41,739 | 16.0 % | 33,951 | 1,972 | 2,553 | 6.12 % |
| — pliegue 4 | 41,738 | 16.0 % | 33,914 | 1,983 | 2,552 | 6.11 % |
| Prueba | 52,173 | 20.0 % | 42,446 | 1,988 | 3,190 | 6.11 % |

- **Usuarios compartidos entre entrenamiento y prueba: 0.** Tampoco los comparten los pliegues entre sí (verificado con aserciones).
- De los vendedores de prueba, 1,986 de 1,988 aparecen en entrenamiento. Esto reproduce la estructura oficial: usuarios nuevos con vendedores conocidos.
- La proporción de positivos es prácticamente idéntica en todas las particiones (6.11–6.12 %).

## 6. Poder predictivo individual (AUC en el conjunto de entrenamiento)

| Familia | Variables | AUC máximo | AUC medio |
|---|---:|---:|---:|
| Vendedor | 16 | 0.622 | 0.547 |
| Par usuario-vendedor | 24 | 0.603 | 0.551 |
| Usuario | 19 | 0.561 | 0.535 |
| Relación | 3 | 0.542 | 0.519 |
| Demográfica | 2 | 0.523 | 0.521 |

**Las 10 mejores variables:** `m_repeat_buyer_rate_log` 0.622, `p_n_items` 0.603, `m_n_repeat_buyers` 0.589, `p_n_cats` 0.587, `p_actions` 0.587, `p_clicks` 0.577, `p_first_days_before` 0.571, `p_purchase` 0.570, `p_actions_pre` 0.566 y `p_n_items_bought` 0.564. Todas tienen relación positiva con la recompra.

### Hallazgos
1. **El vendedor importa tanto como el comprador.** La mejor variable es la fidelidad histórica del vendedor calculada **sin la etiqueta**:
   - Se correlaciona con la tasa real de recompra de cada vendedor (Pearson 0.511 y Spearman 0.425, en 1,323 vendedores con ≥ 30 pares).
   - La tasa de recompra sube por quintiles: Q1 3.3 %, Q2 4.5 %, Q3 5.4 %, Q4 6.9 % y **Q5 10.6 %**.
2. **La antigüedad de la relación cuenta.** Los pares con actividad previa al Double 11 recompran un **7.4 %**, frente a un **5.1 %** de los que conocieron al vendedor ese día.
3. **Perfil del comprador "de oferta".** `p_purchase_rate` y `p_d11_share` tienen relación negativa: los pares cuya actividad se concentra en la compra del 11/11, sin exploración previa, recompran menos.
4. **La demografía es la familia más débil** (AUC ≤ 0.523), como ya mostraba el EDA.
5. **Ninguna variable supera un AUC de 0.63 por sí sola.** Hace falta combinarlas, y la meta de AUC ≥ 0.65 del modelo exige que la combinación aporte más que cualquier variable aislada.

## 7. Archivos generados

| Archivo | Contenido |
|---|---|
| `notebooks/02_ingenieria_variables.ipynb` | Notebook ejecutado (32 celdas) |
| `data/processed/user_log.parquet` | Registro de actividad en parquet (excluido de Git) |
| `data/processed/features_train.parquet` | 260,864 pares: ids, `label`, 64 variables, `split` (`train`/`test`) y `cv_fold` (0–4; −1 en prueba). Excluido de Git |
| `data/processed/features_test.parquet` | 261,477 pares de la prueba de la competencia, sin etiqueta. Se usarán como "datos nuevos" en la aplicación. Excluido de Git |
| `outputs/tables/diccionario_variables.csv` | Nombre, nivel, descripción y AUC individual de cada variable |
| `outputs/tables/auc_individual_variables.csv` | AUC individual y dirección de cada variable |
| `outputs/tables/resumen_particion.csv` | Tamaños y proporción de positivos por partición y pliegue |
| `outputs/figures/17_auc_individual_variables.png` | Las 25 variables con mayor AUC individual, coloreadas por nivel |
