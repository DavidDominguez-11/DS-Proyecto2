# Guía del Proyecto 2. Resultados

**Universidad del Valle de Guatemala**
Facultad de Ingeniería
Departamento de Ciencias de la Computación
**CC3084 – Data Science**
Semestre II – 2026

---

## INTRODUCCIÓN

La Ciencia de Datos permite abordar una gran variedad de problemas complejos. Con el fin de que los estudiantes desarrollen habilidades prácticas, este año se proponen diferentes retos de proyecto. La actividad se realizará en grupos de 4 integrantes, quienes deberán seleccionar uno de los siguientes desafíos:

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

---

## INSTRUCCIONES

### Sobre los Grupos

- Los estudiantes deben inscribirse en los grupos de Canvas para el Proyecto 2. **Si no se inscriben, no recibirán calificación.**

### Sobre los Retos

- Cada grupo debe seleccionar un reto **diferente**. En caso de repetición, se evaluará únicamente la entrega del primer grupo inscrito.

### Sobre el proyecto

- Pueden trabajar en **Google Colab** o **Kaggle**, pero es obligatorio versionar el código en **GitHub**, ya que se evaluarán las contribuciones individuales.

---

## ACTIVIDADES

1. Haga una revisión bibliográfica en la que investigue qué algoritmos de aprendizaje automático se han usado para resolver problemas similares. Puede investigar sobre arquitecturas y modelos diferentes de algún algoritmo en específico. Use el formato APA para referenciar los artículos, de revistas indexadas, que fueron consultados.
2. En base a la investigación revisada, seleccione los algoritmos y/o modelos que usará para resolver su problema.
3. Construya varios modelos con los algoritmos que determinó que serían los más útiles. Si es necesario tunear parámetros hágalo.
4. Pruebe los modelos. Determine su eficiencia. Recuerde que debe usar métricas adecuadas dependiendo de si su problema es de clasificación o de regresión.
5. Discuta sobre los resultados obtenidos con la aplicación de los modelos. Lleve a cabo comparaciones que le permitan seleccionar el o los modelos que usará para resolver su problema.
6. Incluya al menos 3 visualizaciones estáticas que ilustren de una forma gráfica los resultados obtenidos.

### Aplicación

Haga una aplicación en la que se puedan ingresar nuevos datos y el sistema clasifique usando los modelos entrenados.

La aplicación debe:

- **a.** Permitir que el usuario explore las características y variables que tiene el conjunto de datos (luego de las actividades de limpieza), especialmente con las que se crearon los modelos.
- **b.** Permitir al usuario que vea los resultados de cada algoritmo por separado o de todos.
- **c.** Mostrar, de forma informativa, en gráficas interactivas el rendimiento de cada uno de los algoritmos con los datos de prueba. También debe permitir que el usuario decida si esconder o no esa información.

El diseño de la aplicación debe ser intuitivo y amigable con el usuario. Los colores deben ser cuidadosamente seleccionados para que cumpla con la teoría del color estudiada en clase.

### Informe

Elabore un informe en el que reúna toda la información del proyecto. Debe tener las siguientes secciones:

- **Introducción**
  - Se debe introducir el contenido del informe.
  - Se debe plantear el problema a resolver.
- **Objetivos**
  - Tanto general como específicos.
- **Marco Teórico**
  - Debe contener toda la teoría estudiada para elaborar el proyecto.
    - **En caso de procesamiento de imágenes:**
      - Información sobre procesamiento de imágenes.
      - Información teórica sobre análisis de las imágenes desde el punto de vista médico o de la especialidad a la que hacen referencia.
      - Algoritmos de aprendizaje de máquinas, ya sea profundo o no, que serían de utilidad para resolver el problema planteado.
    - **En caso de procesamiento de lenguaje natural:**
      - Definición de procesamiento de lenguaje natural.
      - Actividades de preprocesamiento.
      - Algoritmos usados para procesamiento del lenguaje natural.
    - **En caso de los sistemas de recomendación:**
      - Definición teórica de los sistemas de recomendación.
      - Actividades de preprocesamiento general.
      - Algoritmos usados para sistemas de recomendación.
- **Metodología**
  - Pasos que siguió el grupo para resolver el problema.
  - Explicación de cómo seleccionó el grupo los conjuntos de entrenamiento y prueba.
  - Explicación de la selección de los algoritmos y las razones por las cuales los escogieron.
  - Explicación de selección de las herramientas utilizadas:
    - Recursos de cómputo.
    - Lenguajes de programación, bibliotecas y/o paquetes utilizados.
- **Resultados y Análisis de Resultados**
  - Describe las características del conjunto de datos original.
  - Describe las tareas de limpieza y preprocesamiento a las que tuvo que someter a los datos para lograr los resultados obtenidos.
  - Agrega el análisis exploratorio que se le practicó a los datos. Incluya gráficos que expliquen de manera visual los hallazgos encontrados en esta parte.
  - Explica el ajuste de los parámetros que hubo que hacerle a cada uno de los algoritmos para mejorar el rendimiento y la efectividad.
  - Compara los algoritmos de acuerdo con la efectividad, tiempos de procesamiento, errores, etc. Utiliza para esto gráficos explicativos, estáticos con colores adecuados.
  - Describe la aplicación creada para probar los algoritmos, incluye capturas de pantalla y explica la selección de las tecnologías usadas para construirla.
- **Conclusiones**
  - Explica de qué forma se cumplieron cada uno de los objetivos planteados al inicio y discute sobre la efectividad de los algoritmos seleccionados para resolver el problema planteado.

---

## EVALUACIÓN

> **NOTA:** La evaluación de cada integrante del grupo será de acuerdo con sus contribuciones al trabajo grupal.

- **(15 puntos) Preprocesamiento de los datos de entrada para la aplicación:** Se deben realizar las tareas de preprocesamiento para preparar la entrada para que pueda ser analizada por la aplicación. Esto debe pasar inadvertido para el usuario.

- **(20 puntos) Presentación de resultados en la aplicación:** Se informa el resultado de la clasificación de la entrada al sistema usando modelos entrenados con varios algoritmos. Se puede comparar la eficiencia de cada uno de los modelos basado en la respuesta que da. Se puede seleccionar el modelo a utilizar o utilizarlos todos. La aplicación permite al usuario explorar de forma dinámica e intuitiva los datos.

  > **NOTA:** En la presentación de resultados, no se trata solo de mostrar el rendimiento o la precisión de los modelos entrenados. Es importante que las visualizaciones cuenten la historia detrás de los datos: cómo se comportan, qué patrones o relaciones se descubrieron y cómo se reflejan las predicciones o clasificaciones obtenidas. La comparación entre modelos puede incluir su eficiencia, pero también debe destacar los hallazgos más relevantes del análisis exploratorio y su impacto en la interpretación de los resultados. El objetivo es que las visualizaciones permitan al usuario comprender de forma clara, dinámica e intuitiva el proceso y las conclusiones del proyecto.

- **(15 puntos) Eficiencia de los modelos:** Se elaboran varios modelos con los algoritmos seleccionados. Se muestra la eficiencia de los modelos, usando gráficas interactivas en la aplicación y estáticas en el informe. Se permite al usuario esconder esta información en la aplicación.

- **(40 puntos) Informe final:**
  - El informe tiene todas las secciones que se le solicitan en las instrucciones.
  - Las explicaciones son claras y coherentes.
  - La investigación está completa y bien estructurada.

- **(10 puntos) Referencias y Bibliografía:**
  - Construye la bibliografía consultada, siguiendo las normas APA.
  - Pone referencias consultadas en el texto.
  - La bibliografía referenciada está indexada por lo que es confiable.

---

## MATERIAL A ENTREGAR

- Archivo .pdf con la investigación y discusión de los resultados de los modelos.
- Script de R (.r o .rmd) o de Python que utilizó para responder las preguntas con el código utilizado.
- Link de Google Drive donde trabajó el grupo el informe.
- Link del repositorio usado para versionar el código.
- Presentación a usar para presentar resultados.

---

## FECHAS DE ENTREGA

- **PRESENTACIÓN Y DOCUMENTO FINAL: 12 de octubre de 2026 durante el período de clase**

---

## REFERENCIAS

- <https://www.kaggle.com/general/33266>
- <https://medium.com/analytics-vidhya/how-to-use-google-colab-with-github-via-google-drive-68efb23a42d>
- Para manejar referencias puede usar Mendeley:
  - <https://www.mendeley.com/>
- Puede consultar las fuentes de revistas indexadas que proveen los recursos digitales de la biblioteca:
  - <https://bibliotecas.uvg.edu.gt/recursos/>
  - (IEEE Computer Society) <https://www.computer.org/csdl/home>
    - Este recurso debe ser accedido solo desde la universidad.
