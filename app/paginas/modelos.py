import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_curve

import utils as u

PUNTOS_CURVA = 400


@st.cache_data
def curvas(modelo):
    pred = u.cargar_predicciones_prueba()
    y, p = pred['label'].to_numpy(), pred[f'p_{u.CLAVE_MODELO[modelo]}'].to_numpy()
    fpr, tpr, _ = roc_curve(y, p)
    prec, rec, _ = precision_recall_curve(y, p)
    orden = np.argsort(-p)
    capt = np.concatenate([[0], np.cumsum(y[orden]) / y.sum()])
    submuestra = lambda n: np.unique(np.linspace(0, n - 1, PUNTOS_CURVA).astype(int))
    i_roc, i_pr, i_g = submuestra(len(fpr)), submuestra(len(prec)), submuestra(len(capt))
    return {'roc': (fpr[i_roc], tpr[i_roc]), 'pr': (rec[i_pr], prec[i_pr]),
            'ganancia': (i_g / (len(capt) - 1) * 100, capt[i_g] * 100)}


@st.cache_data
def evaluar_umbral(modelo, fraccion):
    """Métricas si se clasifica como recurrente al `fraccion` de pares con mayor puntaje."""
    pred = u.cargar_predicciones_prueba()
    y, p = pred['label'].to_numpy(), pred[f'p_{u.CLAVE_MODELO[modelo]}'].to_numpy()
    corte = np.quantile(p, 1 - fraccion)
    pred_clase = (p >= corte).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred_clase).ravel()
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return dict(corte=corte, tn=tn, fp=fp, fn=fn, tp=tp, precision=precision, recall=recall, f1=f1,
                contactados=pred_clase.mean())


metadata, _, _ = u.cargar_modelos()
prevalencia = u.cargar_predicciones_prueba()['label'].mean()
n_prueba = len(u.cargar_predicciones_prueba())

st.title('Rendimiento de los modelos')
st.markdown(
    f'Resultados en el **conjunto de prueba**: {n_prueba:,} pares de usuarios que los modelos nunca vieron '
    f'({prevalencia:.1%} recurrentes). Elige qué modelos comparar y, en la barra lateral, qué gráficas mostrar.')

seleccion = st.pills('Modelos', u.MODELOS, selection_mode='multi', default=u.MODELOS, key='modelos_sel')
if not seleccion:
    st.info('Selecciona al menos un modelo.')
    st.stop()
seleccion = [m for m in u.MODELOS if m in seleccion]

with st.sidebar:
    st.subheader('Mostrar u ocultar')
    ver_tabla = st.toggle('Tabla de métricas', value=True)
    ver_curvas = st.toggle('Curvas ROC y precisión-recall', value=True)
    ver_ganancia = st.toggle('Curva de ganancia', value=True)
    ver_umbral = st.toggle('Umbral y matriz de confusión', value=True)
    ver_importancia = st.toggle('Importancia de variables', value=True)
    ver_ajuste = st.toggle('Ajuste de hiperparámetros y tiempos', value=False)

if not any([ver_tabla, ver_curvas, ver_ganancia, ver_umbral, ver_importancia, ver_ajuste]):
    st.info('Todas las gráficas están ocultas. Actívalas desde la barra lateral.', icon=':material/visibility_off:')

# --- Tabla de métricas -------------------------------------------------------
if ver_tabla:
    st.subheader('Métricas en el conjunto de prueba')
    filas = []
    for m in seleccion:
        mt = u.metricas_prueba(m)
        filas.append({'Modelo': m, 'AUC-ROC': mt['auc_roc'], 'AUC-PR': mt['auc_pr'], 'Precisión': mt['precision'],
                      'Recall': mt['recall'], 'F1': mt['f1'], 'Captura top 10 %': mt['captura_top10'],
                      'Exactitud': mt['accuracy'], 'Umbral': mt['umbral'],
                      'Entrenamiento (s)': mt['entrenamiento_s'], 'Predicción (s)': mt['prediccion_s']})
    tabla = pd.DataFrame(filas).set_index('Modelo')
    mejores = ['AUC-ROC', 'AUC-PR', 'Precisión', 'Recall', 'F1', 'Captura top 10 %']
    st.dataframe(tabla.style.format('{:.3f}').highlight_max(subset=mejores, color='#FBE3CC'))
    with st.expander('¿Cómo leer esta tabla?'):
        st.markdown(
            f'- **AUC-ROC** (métrica principal): probabilidad de que el modelo dé mayor puntaje a un recurrente que a '
            f'un no recurrente elegidos al azar. Azar = 0.5.\n'
            f'- **AUC-PR**: resume precisión y recall; con clases desbalanceadas es más exigente. Azar = {prevalencia:.3f}.\n'
            f'- **Precisión, recall y F1** usan el umbral que maximizó F1 en el entrenamiento.\n'
            f'- **Captura top 10 %**: porcentaje de recurrentes alcanzados contactando al 10 % con mayor puntaje (azar = 10 %).\n'
            f'- **La exactitud no sirve para comparar**: predecir siempre "no recurrente" daría {1 - prevalencia:.1%}.\n'
            f'- Los umbrales difieren entre modelos porque la Regresión Logística y Random Forest usan pesos de clase '
            f'balanceados, que desplazan sus puntajes hacia arriba; el del ensamble es un percentil promedio.')

# --- Curvas ROC y PR ---------------------------------------------------------
if ver_curvas:
    st.subheader('Curvas ROC y precisión-recall')
    c1, c2 = st.columns(2)
    fig_roc, fig_pr = go.Figure(), go.Figure()
    for m in seleccion:
        cv = curvas(m)
        estilo_linea = dict(color=u.COLORES_MODELO[m], width=2.5, dash='dash' if m == 'Ensamble' else 'solid')
        fig_roc.add_scatter(x=cv['roc'][0], y=cv['roc'][1], name=f"{m} ({u.metricas_prueba(m)['auc_roc']:.3f})",
                            line=estilo_linea, hovertemplate='FPR %{x:.2f} · TPR %{y:.2f}<extra>' + m + '</extra>')
        fig_pr.add_scatter(x=cv['pr'][0], y=cv['pr'][1], name=f"{m} ({u.metricas_prueba(m)['auc_pr']:.3f})",
                           line=estilo_linea, hovertemplate='Recall %{x:.2f} · Precisión %{y:.2f}<extra>' + m + '</extra>')
    fig_roc.add_scatter(x=[0, 1], y=[0, 1], name='Azar (0.500)', line=dict(color=u.COLOR_REFERENCIA, dash='dot'))
    fig_roc.update_layout(title='Curva ROC', xaxis_title='Tasa de falsos positivos',
                          yaxis_title='Tasa de verdaderos positivos (recall)')
    fig_pr.add_hline(y=prevalencia, line_dash='dot', line_color=u.COLOR_REFERENCIA,
                     annotation_text=f'Azar ({prevalencia:.3f})', annotation_position='bottom right')
    fig_pr.update_layout(title='Curva precisión-recall', xaxis_title='Recall (recurrentes detectados)',
                         yaxis_title='Precisión', yaxis_range=[0, 0.5])
    c1.plotly_chart(u.estilo(fig_roc, 420), key='roc')
    c2.plotly_chart(u.estilo(fig_pr, 420), key='pr')
    st.caption('Las curvas de los cuatro modelos casi se superponen: las diferencias de AUC (≤ 0.005) son del orden '
               'del ruido de la validación cruzada. El límite lo pone la información disponible, no el algoritmo. '
               'La curva precisión-recall se muestra hasta 0.5 de precisión para ver mejor la zona útil.')

# --- Curva de ganancia -------------------------------------------------------
if ver_ganancia:
    st.subheader('¿A cuántos compradores contactar?')
    fig = go.Figure()
    for m in seleccion:
        x, y = curvas(m)['ganancia']
        fig.add_scatter(x=x, y=y, name=m, line=dict(color=u.COLORES_MODELO[m], width=2.5,
                                                   dash='dash' if m == 'Ensamble' else 'solid'),
                        hovertemplate='Contactando al %{x:.0f} %: %{y:.1f} % de los recurrentes<extra>' + m + '</extra>')
    fig.add_scatter(x=[0, 100], y=[0, 100], name='Azar', line=dict(color=u.COLOR_REFERENCIA, dash='dot'))
    fig.update_layout(title='Curva de ganancia acumulada', xaxis_title='% de compradores contactados (mayor puntaje primero)',
                      yaxis_title='% de recurrentes alcanzados')
    st.plotly_chart(u.estilo(fig, 400), key='ganancia')
    x, y = curvas(u.MODELO_PRINCIPAL)['ganancia']
    st.caption(f'Ordenando a los compradores por el puntaje de {u.MODELO_PRINCIPAL}, el primer 10 % contiene al '
               f'{np.interp(10, x, y):.0f} % de los recurrentes y el primer 30 % al {np.interp(30, x, y):.0f} %. '
               'Sin modelo, contactar al 10 % alcanzaría solo al 10 %.')

# --- Umbral interactivo ------------------------------------------------------
if ver_umbral:
    st.subheader('Umbral de decisión y matriz de confusión')
    c1, c2 = st.columns([1, 2])
    with c1:
        modelo_u = st.selectbox('Modelo', seleccion, index=seleccion.index(u.MODELO_PRINCIPAL)
                                if u.MODELO_PRINCIPAL in seleccion else 0)
        mt = u.metricas_prueba(modelo_u)
        fraccion_f1 = (mt['tp'] + mt['fp']) / n_prueba
        porcentaje = st.slider('Porcentaje de compradores a clasificar como "recurrentes"', 1, 60,
                               int(round(fraccion_f1 * 100)), format='%d %%',
                               help=f'Valor inicial: el que resulta del umbral que maximizó F1 ({fraccion_f1:.1%}).')
        r = evaluar_umbral(modelo_u, porcentaje / 100)
        st.metric('Precisión', f"{r['precision']:.1%}", f"{r['precision'] / prevalencia:.1f}× la tasa base",
                  border=True, delta_color='off')
        st.metric('Recall (recurrentes detectados)', f"{r['recall']:.1%}", border=True)
        st.metric('F1', f"{r['f1']:.3f}", border=True)
    with c2:
        cm = np.array([[r['tn'], r['fp']], [r['fn'], r['tp']]])
        pct = cm / cm.sum(axis=1, keepdims=True) * 100
        texto = [[f'{cm[i, j]:,}<br>({pct[i, j]:.1f} %)' for j in range(2)] for i in range(2)]
        fig = go.Figure(go.Heatmap(
            z=pct, x=['Predicho: no recurrente', 'Predicho: recurrente'], y=['Real: no recurrente', 'Real: recurrente'],
            text=texto, texttemplate='%{text}', textfont=dict(size=16), zmin=0, zmax=100, showscale=False,
            colorscale=[[0, '#F2F5F8'], [1, u.COLORES_MODELO[modelo_u]]], hoverinfo='skip'))
        fig.update_layout(title=f'Matriz de confusión — {modelo_u} (clasificando al {porcentaje} % como recurrente)',
                          yaxis_autorange='reversed')
        st.plotly_chart(u.estilo(fig, 400, leyenda_arriba=False), key='confusion')
        st.markdown(f"Clasificando como recurrentes al **{porcentaje} %** de los compradores, de cada 100 marcados "
                    f"unos **{r['precision'] * 100:.0f}** realmente vuelven (al azar serían {prevalencia * 100:.0f}), y se "
                    f"detecta al **{r['recall']:.0%}** de todos los recurrentes. Aumentar el porcentaje detecta más "
                    f"recurrentes pero con menor precisión.")

# --- Importancia de variables ------------------------------------------------
if ver_importancia:
    st.subheader('¿Qué variables usan los modelos?')
    imp = u.cargar_tabla('importancia_variables.csv', index_col=0)
    base = [m for m in seleccion if m in u.MODELOS_BASE]
    if not base:
        st.info('El ensamble no tiene importancia propia: combina los tres modelos base. Selecciona alguno de ellos.')
    else:
        top_n = st.slider('Número de variables', 5, 25, 12)
        cols = st.columns(len(base))
        for col, m in zip(cols, base):
            s = imp[m].reindex(imp[m].abs().sort_values(ascending=False).index[:top_n]).iloc[::-1]
            es_lr = m == 'Regresión Logística'
            colores = [u.COLORES_MODELO[m] if (v >= 0 or not es_lr) else u.COLOR_NO_RECURRENTE for v in s]
            fig = go.Figure(go.Bar(x=s.values, y=s.index, orientation='h', marker_color=colores,
                                   hovertemplate='%{y}: %{x:.3f}<extra></extra>'))
            fig.update_layout(title=m, xaxis_title='Coeficiente (variable estandarizada)' if es_lr
                              else '% de la importancia total')
            col.plotly_chart(u.estilo(fig, 120 + 28 * top_n, leyenda_arriba=False), key=f'imp_{m}')
        st.caption('`m_target_encoding` es la tasa de recompra histórica del vendedor (calculada sin fuga). En la '
                   'Regresión Logística, las barras grises son coeficientes negativos (la variable reduce la '
                   'probabilidad de recompra, manteniendo constantes las demás). Hallazgo principal: **el vendedor '
                   'importa tanto como el comprador**, seguido de la profundidad y antigüedad de la relación, tal '
                   'como anticipaba el análisis exploratorio.')

# --- Ajuste y tiempos --------------------------------------------------------
if ver_ajuste:
    st.subheader('Ajuste de hiperparámetros y tiempos de cómputo')
    ajuste = u.cargar_tabla('ajuste_hiperparametros.csv').set_index('modelo')
    base = [m for m in seleccion if m in ajuste.index] or list(ajuste.index)
    if base != [m for m in seleccion if m in ajuste.index]:
        st.caption('El ensamble no tiene hiperparámetros propios; se muestran los tres modelos base.')
    c1, c2 = st.columns(2)
    fig = go.Figure()
    fig.add_bar(x=base, y=ajuste.loc[base, 'auc_cv_defecto'], name='Por defecto', marker_color='#C5CDD5')
    fig.add_bar(x=base, y=ajuste.loc[base, 'auc_cv_ajustado'], name='Ajustado',
                marker_color=[u.COLORES_MODELO[m] for m in base])
    fig.update_layout(title='AUC-ROC de validación cruzada', yaxis_range=[0.6, 0.71], barmode='group')
    c1.plotly_chart(u.estilo(fig, 360), key='ajuste')
    tiempos = pd.DataFrame({m: {k: u.metricas_prueba(m)[k] for k in ['busqueda_min', 'entrenamiento_s', 'prediccion_s']}
                            for m in seleccion}).T
    fig = go.Figure()
    fig.add_bar(x=tiempos.index, y=tiempos['entrenamiento_s'], marker_color=[u.COLORES_MODELO[m] for m in tiempos.index],
                text=[f'{v:.1f} s' for v in tiempos['entrenamiento_s']], textposition='outside')
    fig.update_layout(title='Tiempo de entrenamiento final (208,691 pares)', yaxis_title='segundos', showlegend=False)
    c2.plotly_chart(u.estilo(fig, 360), key='tiempos')
    vista = ajuste.loc[base, ['auc_cv_defecto', 'auc_cv_ajustado', 'mejora', 'auc_train_ajustado',
                              'configuraciones_probadas', 'tiempo_busqueda_min', 'mejores_hiperparametros']]
    vista['mejores_hiperparametros'] = vista['mejores_hiperparametros'].map(
        lambda s: ', '.join(f'{k} = {v}' for k, v in json.loads(s).items()))
    st.dataframe(vista, column_config={
        'auc_cv_defecto': st.column_config.NumberColumn('AUC CV por defecto', format='%.4f'),
        'auc_cv_ajustado': st.column_config.NumberColumn('AUC CV ajustado', format='%.4f'),
        'mejora': st.column_config.NumberColumn('Mejora', format='%+.4f'),
        'auc_train_ajustado': st.column_config.NumberColumn('AUC entrenamiento', format='%.3f'),
        'configuraciones_probadas': 'Configuraciones', 'tiempo_busqueda_min': st.column_config.NumberColumn(
            'Búsqueda (min)', format='%.1f'),
        'mejores_hiperparametros': st.column_config.TextColumn('Mejores hiperparámetros', width='large')})
    st.caption('Random Forest es el que más gana con el ajuste: por defecto memoriza el entrenamiento (AUC 1.0 en '
               'entrenamiento). Los tiempos varían entre ejecuciones según la carga del equipo.')
