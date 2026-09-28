# Aplicación Interactiva

Este documento describe la aplicación (paso 9 de `07_metodologia_modelado.md`) que permite explorar los datos, comparar el rendimiento de los modelos y clasificar nuevos pares usuario-vendedor.

---

## 1. Tecnologías y justificación

| Tecnología | Versión | Por qué se eligió |
|---|---|---|
| **Streamlit** | 1.64.0 | Aplicación web escrita en Python. Carga directamente los `Pipeline` de scikit-learn y LightGBM entrenados, sin reescribir el preprocesamiento en otro lenguaje ni montar una API. Trae componentes interactivos (filtros, interruptores, formularios, carga de archivos) y caché de datos y modelos. |
| **Plotly** | 7.1.0 | Gráficas interactivas (zoom, *hover* con valores, ocultar series desde la leyenda) que se integran de forma nativa con Streamlit. |
| **pandas, NumPy, scikit-learn, LightGBM, joblib** | las de `requirements.txt` | Las mismas bibliotecas del entrenamiento: la aplicación aplica exactamente las mismas transformaciones. |

Alternativas descartadas:
- **Dash**: requiere más código de estructura (*callbacks*) para el mismo resultado.
- **Shiny para R**: el proyecto está en Python.
- **Frontend web con una API**: sale de lo que el proyecto necesita y del tiempo disponible.

## 2. Estructura

```
.streamlit/config.toml       # Tema (colores) de la aplicación
app/
├── app.py                   # Punto de entrada y navegación entre páginas
├── utils.py                 # Rutas, paleta, carga en caché, predicción y construcción de filas
├── preparar_datos.py        # Genera app/data a partir de data/processed
├── data/                    # Datos compactos de la aplicación (~29 MB)
│   ├── pares_etiquetados.parquet   # 260,864 pares con etiqueta, split y 64 variables
│   ├── pares_competencia.parquet   # 261,477 pares de la prueba oficial (sin etiqueta)
│   ├── vendedores.parquet          # Variables m_ y tasa de recompra de entrenamiento por vendedor
│   └── perfiles_usuario.parquet    # 4 usuarios reales representativos (percentil 25/50/75/90 de actividad)
└── paginas/
    ├── inicio.py
    ├── exploracion.py
    ├── modelos.py
    └── prediccion.py
```

- **Modelos y resultados:** la aplicación los lee de `outputs/models/` (los tres `Pipeline`, `metadata.json`, las predicciones de prueba y la referencia del ensamble) y las tablas de `outputs/tables/`.
- **Independencia del registro de actividad:** no depende del archivo de 1.9 GB. Todas las variables ya están calculadas en `app/data/`.

**Ejecución** (desde la raíz del repositorio, con el entorno virtual):

```bash
.venv/Scripts/python app/preparar_datos.py          # solo si se regeneraron los datos del notebook 02
.venv/Scripts/python -m streamlit run app/app.py
```

## 3. Páginas y requisitos cubiertos

### 3.1 Inicio — la historia de los datos

- **Indicadores clave**:
  - 260,864 compradores nuevos, de los cuales el 6.1 % volvió a comprar.
  - AUC-ROC de LightGBM: 0.689.
  - Captura del 27 % de los recurrentes contactando solo al 10 % de los compradores, 2.7 veces más que al azar.
- **"La historia en cuatro gráficas"**, que conecta el análisis exploratorio con los modelos:
  1. **El Double 11 concentra las compras**: compras por día en escala logarítmica; el 11/11 reúne el 37 %.
  2. **El vendedor importa**: tasa de recompra por quintil de fidelidad histórica de la clientela del vendedor. Va de 3.4 % a 10.5 %, 3.1 veces más.
  3. **La relación previa y la exploración importan**: tasa de recompra según los productos explorados, separando a quienes ya visitaban al vendedor antes del 11/11. Con 10 o más productos y actividad previa llega a ~12.5 %.
  4. **El modelo ordena a los compradores**: curva de ganancia de LightGBM frente al azar.
- **Conclusión y accesos directos** a las demás páginas.

### 3.2 Exploración de datos — requisito (a)

Permite explorar las variables del conjunto de datos después de la limpieza, en particular las 64 con las que se entrenaron los modelos.

- **Variables numéricas**:
  - Se elige el nivel (par, usuario, vendedor, relación) y la variable, ordenadas por AUC individual y con su descripción.
  - Indicadores: AUC individual, dirección de la relación y mediana por clase.
  - Tasa de recompra por deciles de la variable, con la tasa promedio como referencia.
  - Distribución por clase con interruptores de escala logarítmica y de recorte al percentil 99.
  - Diagrama de caja por clase.
- **Edad y género**: tasa de recompra y número de pares por categoría.
- **Correlaciones**: mapa de calor Spearman o Pearson de las variables elegidas, con o sin la etiqueta.
- **Diccionario de variables**: tabla filtrable por nivel y por texto, con el AUC individual como barra. Incluye una muestra de la tabla de modelado.

### 3.3 Rendimiento de los modelos — requisitos (b) y (c)

- **Selección de modelos**: se elige uno, varios o todos (Regresión Logística, Random Forest, LightGBM, Ensamble). Todas las gráficas se actualizan con la selección. → **(b)**
- **Interruptores en la barra lateral** para **mostrar u ocultar** cada bloque de información. → **(c)**
  - Tabla de métricas en prueba, con el mejor valor resaltado y una guía de lectura.
  - Curvas ROC y precisión-recall.
  - Curva de ganancia ("¿a cuántos compradores contactar?").
  - **Umbral interactivo**: un deslizador fija qué porcentaje de compradores se clasifica como recurrente, y se actualizan la matriz de confusión, la precisión (con cuántas veces supera a la tasa base), el recall, F1 y una interpretación en lenguaje natural.
  - Importancia de variables de cada modelo, con número de variables configurable y coeficientes negativos de la Regresión Logística en gris.
  - Ajuste de hiperparámetros (defecto frente a ajustado) y tiempos de entrenamiento.
- **Todas las gráficas son interactivas (Plotly)** y se calculan con las predicciones reales sobre los 52,173 pares de prueba.

### 3.4 Clasificar compradores — ingreso de datos nuevos

**Tres formas de ingresar datos:**

1. **Buscar un par**:
   - *Prueba (con respuesta conocida)*: pares reservados para evaluar. La aplicación muestra también si el comprador realmente volvió.
   - *Competencia (sin respuesta)*: pares de `test_format1.csv`, datos realmente nuevos.
   - Se elige el `user_id` y uno de sus vendedores, o un par al azar.
2. **Ingresar datos manualmente**: el usuario llena un formulario con lo esencial:
   - vendedor, edad, género y nivel de actividad general;
   - clics, favoritos y carrito antes del 11/11, días con actividad previa, y días desde la primera y la última visita;
   - clics, favoritos, carrito y compras del 11/11, y productos, categorías y marcas distintos.
3. **Clasificar un archivo**: se sube un CSV con `user_id` y `merchant_id` (se ofrece un archivo de ejemplo). La aplicación clasifica los pares encontrados, indica cuáles no existen y de qué conjunto proviene cada uno, avisa si hay pares de entrenamiento (predicción optimista) y permite descargar los resultados.

**Preprocesamiento transparente** (rubro de 15 puntos). El usuario nunca transforma datos:
- En las opciones 1 y 3, las 64 variables se toman de los datos precalculados.
- En la opción 2, `construir_fila_manual` deriva las 64 variables:
  - Variables del par: se calculan a partir de los conteos ingresados (totales, tasas, proporción del 11/11, indicador de actividad previa).
  - Variables del vendedor: se toman del perfil real del vendedor elegido.
  - Variables del usuario: se toman de un usuario real con el nivel de actividad elegido, ajustado para que su actividad total no sea menor que la del par.
  - Variables de relación: se recalculan.
- El formulario corrige combinaciones imposibles y avisa en cada caso (por ejemplo, más categorías que productos, o actividad previa sin días de actividad).
- Luego se aplica el mismo `Pipeline` del entrenamiento: `log1p`, estandarización, *one-hot* y *target encoding* del vendedor.

**Presentación de resultados** (rubro de 20 puntos). Para cada modelo elegido (uno o todos) se muestra una tarjeta con:
- **Clase**: *recurrente probable* o *no recurrente probable*, según el umbral del modelo.
- **Percentil** del puntaje entre los compradores de prueba. Es comparable entre modelos.
- **Tasa real de recompra en su decil de puntaje**: la lectura más honesta de "probabilidad".
- **Puntaje y umbral**.

Además:
- Una gráfica compara la posición del comprador en cada modelo con el umbral respectivo.
- Una tabla explica el resultado: tasa histórica de recompra del vendedor y valores del comprador en las variables más importantes, con su percentil y la mediana de recurrentes y no recurrentes.

**Por qué no se muestra el puntaje como probabilidad.** La Regresión Logística y Random Forest se entrenaron con pesos de clase balanceados, que desplazan sus puntajes hacia arriba: un puntaje de 0.6 no significa 60 % de probabilidad cuando la tasa base es 6 %. El percentil y la tasa del decil sí son comparables e interpretables.

## 4. Diseño y teoría del color

| Elemento | Color | Justificación |
|---|---|---|
| Color principal (botones, barras neutras, tema) | Azul `#1F5F8B` | Tono frío asociado con confianza y análisis. Buen contraste sobre fondo blanco. |
| Clase de interés: recurrente | Naranja `#E07A1F` | **Complementario** del azul principal: atrae la atención hacia la clase minoritaria que se busca identificar. |
| Clase mayoritaria: no recurrente | Gris azulado `#8C9BAB` | Neutro y poco saturado, para no competir con la clase de interés. |
| Referencias (azar, promedio) | Gris `#6B7785`, líneas punteadas | Contexto sin protagonismo. |
| Modelos | Paleta **Okabe-Ito** (azul `#0072B2`, verde `#009E73`, bermellón `#D55E00`, púrpura `#CC79A7`) | Distinguible para personas con daltonismo. Es la misma que usan las figuras estáticas de los notebooks, así cada modelo tiene siempre el mismo color. |
| Correlaciones | Escala divergente rojo-azul centrada en 0 | Distingue asociaciones positivas y negativas con igual intensidad visual. |
| Fondo | Blanco `#FFFFFF` con paneles `#F2F5F8` | Alta legibilidad; los paneles agrupan contenido sin bordes pesados. |

**Principios de usabilidad aplicados**:
- Cada página empieza con una explicación breve.
- Cada gráfica tiene título, ejes con unidades y un pie que explica qué observar.
- Las opciones avanzadas están en desplegables ("¿Cómo leer esta tabla?", "¿Por qué este resultado?").
- La navegación lateral tiene íconos.
- Los textos generados a partir de los datos (por ejemplo, "3.1 veces más") se calculan en vivo y no se escriben a mano.

## 5. Pruebas

- **Pruebas automáticas** con `streamlit.testing.v1.AppTest`: las cuatro páginas cargan sin excepciones. También se probaron sin errores estas interacciones:
  - formulario manual con valores incoherentes (se corrigen con avisos);
  - par al azar con respuesta real;
  - origen *competencia*;
  - ocultar todas las gráficas;
  - seleccionar solo el ensamble;
  - cambiar el nivel y la variable, y desactivar la escala logarítmica en la exploración.
- **Clasificación por archivo**: se verificó que encuentra los pares, reporta los inexistentes, identifica el origen de cada par y que sus predicciones coinciden exactamente con las guardadas en `predicciones_prueba.parquet`.
- **Revisión visual con capturas de Chrome sin interfaz**: se corrigieron tres defectos que las pruebas automáticas no detectan:
  - el título y la leyenda de varias gráficas se encimaban (se reserva margen superior cuando hay ambos);
  - el diagrama de caja dibujaba las dos clases superpuestas (ahora cada clase tiene su posición);
  - la tabla "¿Por qué este resultado?" no se mostraba dentro del desplegable (se cambió a una tabla estática).
- Se agregó el parámetro `?pestana=manual` (o `archivo`) en la URL de la página de clasificación para abrir directamente esa pestaña, útil en la demostración.
- **Revisión visual en el navegador (primera versión)**: permitió corregir dos defectos:
  - Plotly interpretaba los tramos "1, 2, 3–4…" como números y omitía los no numéricos; se forzó un eje categórico.
  - El pico del 11/11 aplastaba la serie diaria; se usó escala logarítmica.

## 6. Capturas de la aplicación

Capturas tomadas con la aplicación en ejecución (Chrome sin interfaz, ventana de 1600 px de ancho) y guardadas en `outputs/figures/app/`. La pestaña del formulario se abre directamente con `?pestana=manual` en la URL de la página de clasificación:

| Archivo | Contenido sugerido |
|---|---|
| `outputs/figures/app/01_inicio.png` | Página de inicio: indicadores y las cuatro gráficas |
| `outputs/figures/app/02_exploracion.png` | Exploración: una variable (p. ej. `m_repeat_buyer_rate_log`) con tasa por deciles, distribución y caja |
| `outputs/figures/app/03_modelos.png` | Rendimiento: selección de modelos, barra lateral de interruptores y curvas ROC/PR |
| `outputs/figures/app/04_umbral.png` | Rendimiento: umbral interactivo y matriz de confusión |
| `outputs/figures/app/05_prediccion.png` | Clasificación: resultado de un par con las tarjetas de los cuatro modelos y la explicación |
| `outputs/figures/app/06_formulario.png` | Clasificación: formulario de ingreso manual |
