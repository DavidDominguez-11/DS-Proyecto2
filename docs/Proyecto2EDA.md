# Guía del Proyecto 2. Análisis Exploratorio

**Universidad del Valle de Guatemala**
**Facultad de Ingeniería**
**Departamento de Ciencias de la Computación**
**CC3084 – Data Science**
**Semestre II – 2026**

---

## Introducción

Dado que existen tantos problemas complejos que se pueden atacar con la Ciencia de Datos, es por esto por lo que este año se plantean alternativas de proyecto. La actividad se realizará en grupos de 4 personas que deberán seleccionar uno de los siguientes retos:

| # | Reto | Tema |
|---|------|------|
| 1 | [Biohub - Cell Tracking During Development](https://www.kaggle.com/competitions/biohub-cell-tracking-during-development) | Visión Artificial |
| 2 | [Trace the Ace](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/) | Procesamiento del Lenguaje Natural |
| 3 | [A Step Ahead of Drought: Forecasting Global Water Storage Challenge by ITU](https://zindi.africa/competitions/one-step-ahead-of-drought-forecasting-global-water-storage-challenge) | Series de tiempo con datos satelitales |
| 4 | [Jigsaw - Agile Community Rules Classification](https://www.kaggle.com/competitions/jigsaw-agile-community-rules/overview) | Procesamiento del Lenguaje Natural |
| 5 | [MITSUI&CO. Commodity Prediction Challenge](https://www.kaggle.com/competitions/mitsui-commodity-prediction-challenge/overview) | Series de tiempo |
| 6 | [MAP - Charting Student Math Misunderstandings](https://www.kaggle.com/competitions/map-charting-student-math-misunderstandings/overview) | Procesamiento del Lenguaje Natural |
| 7 | [RSNA Intracranial Aneurysm Detection](https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/overview) | Visión Artificial |
| 8 | [NeurIPS - Desafío de datos Ariel 2024](https://www.kaggle.com/competitions/ariel-data-challenge-2024/data) | Visión Artificial |
| 9 | [Clasificación degenerativa de la columna lumbar RSNA 2024](https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification) | Visión Artificial |
| 10 | [Predecir qué respuesta preferirá un usuario en esta batalla cara a cara con datos del Chatbot Arena](https://www.kaggle.com/competitions/lmsys-chatbot-arena) | Procesamiento del Lenguaje Natural |
| 11 | [Predicción de compradores recurrentes: cuestionar la línea base](https://tianchi.aliyun.com/competition/entrance/231576/information) | Negocios |
| 12 | [CommonLit - Evaluar resúmenes de estudiantes](https://www.kaggle.com/competitions/commonlit-evaluate-student-summaries/overview) | Procesamiento del Lenguaje Natural |
| 13 | [Detección de estructuras microvasculares en tejidos de riñón humano sanos](https://www.kaggle.com/competitions/hubmap-hacking-the-human-vasculature/overview) | Visión Artificial |
| 14 | [Detectar y clasificar lesiones abdominales traumáticas](https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/data?select=train_series_meta.csv) | Visión Artificial |
| 15 | [Google: reconocimiento de deletreo manual del lenguaje de señas estadounidense](https://www.kaggle.com/competitions/asl-fingerspelling) | Visión Artificial |
| 16 | [Desafío Ojos en el Terreno del CGIAR. Detección de enfermedades en plantas](https://zindi.africa/competitions/cgiar-eyes-on-the-ground-challenge) | Visión Artificial |
| 17 | [Identificación de Especies de Mosquitos](https://www.aicrowd.com/challenges/mosquitoalert-challenge-2023) | Visión Artificial |
| 18 | [Hackeando el cuerpo humano](https://www.kaggle.com/competitions/hubmap-organ-segmentation/overview) | Visión Artificial |
| 19 | [Predicción de argumentos efectivos](https://www.kaggle.com/competitions/feedback-prize-effectiveness) | Procesamiento del Lenguaje Natural |
| 20 | [Detección de fracturas de las vértebras cervicales en radiografías](https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/overview) | Visión Artificial |
| 21 | [Detección de pases en videos de jugadas de football de la liga alemana](https://www.kaggle.com/competitions/dfl-bundesliga-data-shootout) | Visión Artificial |
| 22 | [Clasificación de los orígenes de un coágulo de sangre en un accidente cerebrovascular](https://www.kaggle.com/competitions/mayo-clinic-strip-ai) | Visión Artificial |
| 23 | [Identificación de menciones de entidades biomédicas en resúmenes de artículos de investigación](https://bitgrit.net/competition/13) | Procesamiento del Lenguaje Natural |
| 24 | [Identificación de relaciones de entidades biomédicas en resúmenes de artículos de investigación](https://bitgrit.net/competition/14) | Procesamiento del Lenguaje Natural |

> **Nota:** Los primeros 3 retos son competencias activas.

---

## Instrucciones

### Sobre los grupos
- Deben inscribirse a alguno de los grupos de Canvas para el Proyecto 2.
- **Si no se inscribe en algún grupo no será calificado.**

### Sobre los retos
- Cada grupo debe seleccionar un reto diferente; no pueden repetirse.
- Si esto sucediera, se revisará la entrega del primer grupo que la realice.

### Sobre el proyecto
- Puede usar los recursos que Kaggle o Google Colab le proporciona, pero debe versionarlo en GitHub, puesto que sus contribuciones se usarán para la evaluación individual de cada miembro del grupo.

---

## Actividades

1. **Investigación del tema:** haga una pequeña investigación del tema para tener idea de qué buscar en un análisis exploratorio.
   - Problemas médicos: describa la enfermedad a detectar, los síntomas y cómo se diagnostica (especialmente diagnóstico basado en imágenes). Esto ayuda a entender el patrón que deben reconocer los algoritmos.
   - Problemas de Procesamiento del Lenguaje Natural: investigue las técnicas que se usan para detectar patrones en lenguaje escrito.
   - Problemas de negocios: investigue qué técnicas se usan para mejorar la retención de clientes y las ofertas.
2. Analice el problema planteado y los datos.
3. Describa las tareas de limpieza y preprocesamiento que llevó a cabo.
4. Haga un análisis exploratorio de los datos:
   1. Comience describiendo cuántas variables y observaciones tiene disponible, y el tipo de cada una de las variables.
   2. Haga un resumen de las variables numéricas y tablas de frecuencia para las variables categóricas; escriba lo que vaya encontrando, si aplica.
   3. Cruce las variables que considere más importantes para hallar los elementos clave que puedan ayudar a comprender lo que está causando el problema encontrado.
   4. Haga gráficos exploratorios que den ideas del estado de los datos.
5. Escriba unas conclusiones con los hallazgos encontrados durante el análisis exploratorio.

---

## Evaluación

> **Nota:** La evaluación de cada integrante del grupo será de acuerdo con sus contribuciones al trabajo grupal.

| Rubro | Puntos | Descripción |
|-------|--------|-------------|
| Situación Problemática | 10 | Describe la situación problemática que da lugar al problema. |
| Problema científico | 10 | Se enuncia el problema científico que se desprende de la situación planteada. Se comprende bien cuál es el problema. |
| Objetivos | 10 | Se plantean los objetivos a cumplir para darle solución al problema planteado. Se enuncia al menos un objetivo general y 2 específicos. Los objetivos deben ser medibles y alcanzables durante la investigación. |
| Descripción de los datos | 20 | Se describen los datos, tanto las variables y observaciones como las operaciones de limpieza que se hicieron si fueron necesarias. |
| Análisis Exploratorio | 30 | - Estudia las variables cuantitativas mediante técnicas de estadística descriptiva.<br>- Hace gráficos exploratorios como histogramas, diagramas de cajas y bigotes, gráficos de dispersión que ayudan a explicar los datos.<br>- Analiza las correlaciones entre las variables, trata de explicar los outliers (puntos atípicos) y toma decisiones acertadas ante la presencia de valores faltantes.<br>- Estudia las variables categóricas.<br>- Elabora gráficos de barra, tablas de frecuencia y de proporciones.<br>- Explica muy bien todos los procedimientos y los hallazgos que va haciendo. |
| Hallazgos y conclusiones | 20 | - Hace un resumen de los hallazgos en el análisis exploratorio.<br>- Llega a conclusiones sobre los siguientes pasos a seguir. |

**Total: 100 puntos**

---

## Material a entregar

- Archivo `.pdf` con el informe de análisis exploratorio.
- Link del repositorio usado para versionar el código y/o link de Kaggle o Google Colab en caso de que los utilice.
- Presentación de PowerPoint a usar para presentar resultados.

---

## Fechas de entrega

- **Presentación y documento final completo:** 11 de septiembre de 2025 *(nota: el documento indica 2025; verificar si corresponde a 2026 dado el contexto del semestre)*

---

## Referencias

- [https://www.kaggle.com/general/33266](https://www.kaggle.com/general/33266)
- [https://medium.com/analytics-vidhya/how-to-use-google-colab-with-github-via-google-drive-68efb23a42d](https://medium.com/analytics-vidhya/how-to-use-google-colab-with-github-via-google-drive-68efb23a42d)
