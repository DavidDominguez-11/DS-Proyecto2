import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import utils as u


@st.cache_data
def datos_historia():
    pares = u.cargar_pares()
    tasa_base = pares['label'].mean()

    diaria = u.cargar_tabla('actividad_diaria.csv', index_col=0)
    diaria['total'] = diaria.sum(axis=1)
    diaria['fecha'] = [f'{ts % 100:02d}/{ts // 100:02d}' for ts in diaria.index]

    quintil = pd.qcut(pares['m_repeat_buyer_rate_log'], 5,
                      labels=['Q1\nmenos fiel', 'Q2', 'Q3', 'Q4', 'Q5\nmás fiel'])
    por_vendedor = pares.groupby(quintil, observed=True)['label'].agg(['mean', 'size'])

    tramos = pd.cut(pares['p_n_items'], [0, 1, 2, 4, 9, np.inf], labels=['1', '2', '3–4', '5–9', '10+'])
    previa = pares['p_has_pre'].map({0: 'Lo conoció el 11/11', 1: 'Ya lo visitaba antes'})
    por_relacion = pares.groupby([previa, tramos], observed=True)['label'].agg(['mean', 'size']).reset_index()
    por_relacion.columns = ['previa', 'tramo', 'tasa', 'pares']
    return tasa_base, diaria, por_vendedor, por_relacion


@st.cache_data
def curva_ganancia(modelo):
    pred = u.cargar_predicciones_prueba()
    p = pred[f'p_{u.CLAVE_MODELO[modelo]}'].to_numpy()
    y = pred['label'].to_numpy()[np.argsort(-p)]
    x = np.linspace(0, 1, 201)
    capturados = np.concatenate([[0], np.cumsum(y) / y.sum()])
    idx = (x * len(y)).astype(int)
    return x * 100, capturados[idx] * 100


pares = u.cargar_pares()
tasa_base, diaria, por_vendedor, por_relacion = datos_historia()
m_principal = u.metricas_prueba(u.MODELO_PRINCIPAL)

st.title('¿Volverá a comprar?')
st.markdown(
    'Durante el **Double 11** (11 de noviembre) miles de usuarios compran por primera vez a un vendedor de '
    'Tmall atraídos por los descuentos, pero muy pocos regresan. Esta aplicación resume el análisis de '
    '**55 millones de interacciones** y los modelos de clasificación entrenados para identificar, entre esos '
    'compradores nuevos, a los que tienen más probabilidad de **volver a comprar al mismo vendedor** en los '
    'seis meses siguientes.')

c1, c2, c3, c4 = st.columns(4)
c1.metric('Compradores nuevos', f'{len(pares):,}', border=True,
          help='Pares (usuario, vendedor) del conjunto de entrenamiento de la competencia.')
c2.metric('Volvieron a comprar', f'{tasa_base:.1%}', border=True,
          help='Clase minoritaria: el problema está muy desbalanceado.')
c3.metric(f'AUC-ROC ({u.MODELO_PRINCIPAL})', f"{m_principal['auc_roc']:.3f}", border=True,
          help='En el conjunto de prueba. 0.5 = azar; 1 = separación perfecta. Evaluado con usuarios que el modelo nunca vio.')
c4.metric('Captura contactando al 10 %', f"{m_principal['captura_top10']:.0%}",
          delta=f"{m_principal['captura_top10'] / 0.10:.1f} veces más que al azar", border=True,
          help='Porcentaje de los compradores recurrentes que se alcanzan contactando solo al 10 % con mayor puntaje.')

st.subheader('La historia en cuatro gráficas')
col1, col2 = st.columns(2, gap='large')

with col1:
    st.markdown('**1. El Double 11 concentra las compras.** Ese día ocurre el '
                f"{diaria.loc[1111, 'purchase'] / diaria['purchase'].sum():.0%} de todas las compras del periodo: "
                'los compradores analizados llegaron atraídos por la promoción.')
    fig = go.Figure()
    fig.add_bar(x=diaria['fecha'], y=diaria['purchase'],
                marker_color=np.where(diaria.index == 1111, u.COLOR_RECURRENTE, u.COLOR_NO_RECURRENTE),
                hovertemplate='%{x}: %{y:,} compras<extra></extra>')
    fig.add_annotation(x='11/11', y=np.log10(diaria.loc[1111, 'purchase']), text='Double 11',
                       showarrow=True, arrowhead=2, ax=-60, ay=10, font=dict(color=u.COLOR_RECURRENTE))
    fig.update_layout(xaxis=dict(title='Día (dd/mm)', nticks=12), bargap=0,
                      yaxis=dict(title='Compras por día (escala logarítmica)', type='log'))
    st.plotly_chart(u.estilo(fig, 330), key='historia_diaria')

with col2:
    razon = por_vendedor['mean'].iloc[-1] / por_vendedor['mean'].iloc[0]
    st.markdown('**2. El vendedor importa.** Los vendedores cuya clientela histórica ya repetía compras '
                f'retienen {razon:.1f} veces más a los compradores nuevos que los menos fieles.')
    fig = go.Figure(go.Bar(
        x=por_vendedor.index.astype(str).str.replace('\n', '<br>'), y=por_vendedor['mean'] * 100,
        marker_color=[u.COLOR_NO_RECURRENTE] * 4 + [u.COLOR_RECURRENTE],
        customdata=por_vendedor['size'], text=[f'{v:.1%}' for v in por_vendedor['mean']], textposition='outside',
        hovertemplate='%{x}<br>Tasa de recompra: %{y:.1f} %<br>Pares: %{customdata:,}<extra></extra>'))
    fig.add_hline(y=tasa_base * 100, line_dash='dot', line_color=u.COLOR_REFERENCIA,
                  annotation_text=f'Promedio {tasa_base:.1%}', annotation_position='top left')
    fig.update_layout(xaxis_title='Quintil de fidelidad histórica de la clientela del vendedor',
                      yaxis_title='Tasa de recompra (%)', yaxis_range=[0, por_vendedor['mean'].max() * 125])
    st.plotly_chart(u.estilo(fig, 330), key='historia_vendedor')

col3, col4 = st.columns(2, gap='large')
with col3:
    st.markdown('**3. La relación previa y la exploración importan.** Quien ya visitaba al vendedor antes del '
                '11/11 y exploró más productos vuelve más.')
    fig = go.Figure()
    for grupo, color in [('Lo conoció el 11/11', u.COLOR_NO_RECURRENTE), ('Ya lo visitaba antes', u.COLOR_RECURRENTE)]:
        d = por_relacion[por_relacion['previa'] == grupo]
        fig.add_scatter(x=d['tramo'].astype(str), y=d['tasa'] * 100, mode='lines+markers', name=grupo,
                        line=dict(color=color, width=3), marker=dict(size=9), customdata=d['pares'],
                        hovertemplate='%{x} productos: %{y:.1f} %<br>Pares: %{customdata:,}<extra>' + grupo + '</extra>')
    fig.add_hline(y=tasa_base * 100, line_dash='dot', line_color=u.COLOR_REFERENCIA)
    fig.update_layout(xaxis=dict(title='Productos distintos del vendedor que exploró', type='category'),
                      yaxis_title='Tasa de recompra (%)')
    st.plotly_chart(u.estilo(fig, 330), key='historia_relacion')

with col4:
    st.markdown(f'**4. El modelo ordena a los compradores.** Si el vendedor solo pudiera contactar al 10 % con mayor '
                f"puntaje de {u.MODELO_PRINCIPAL}, alcanzaría al {m_principal['captura_top10']:.0%} de los que "
                'realmente vuelven.')
    x, y = curva_ganancia(u.MODELO_PRINCIPAL)
    fig = go.Figure()
    fig.add_scatter(x=x, y=y, name=u.MODELO_PRINCIPAL, line=dict(color=u.COLORES_MODELO[u.MODELO_PRINCIPAL], width=3),
                    hovertemplate='Contactando al %{x:.0f} %: %{y:.1f} % de los recurrentes<extra></extra>')
    fig.add_scatter(x=[0, 100], y=[0, 100], name='Al azar', line=dict(color=u.COLOR_REFERENCIA, dash='dot'))
    fig.add_annotation(x=10, y=m_principal['captura_top10'] * 100, text=f"10 % → {m_principal['captura_top10']:.0%}",
                       showarrow=True, arrowhead=2, ax=50, ay=30)
    fig.update_layout(xaxis_title='% de compradores contactados (mayor puntaje primero)',
                      yaxis_title='% de recurrentes alcanzados')
    st.plotly_chart(u.estilo(fig, 330), key='historia_ganancia')

aucs = [u.metricas_prueba(m)['auc_roc'] for m in u.MODELOS]
st.info('**Conclusión:** la recompra no depende de una sola variable, sino de la combinación de **quién es el '
        'vendedor**, **qué tan profunda y antigua es la relación** del usuario con él y **los hábitos del usuario** '
        'en la plataforma. La demografía aporta poco. Los cuatro modelos probados alcanzan un AUC-ROC de '
        f'{min(aucs):.3f}–{max(aucs):.3f} con usuarios nuevos.', icon=':material/lightbulb:')

st.subheader('¿Qué puedo hacer en esta aplicación?')
a, b, c = st.columns(3)
with a.container(border=True):
    st.markdown('**Explorar los datos**  \nDistribución de cada una de las 64 variables de los modelos, su relación '
                'con la recompra y sus correlaciones.')
    st.page_link('paginas/exploracion.py', label='Ir a exploración', icon=':material/query_stats:')
with b.container(border=True):
    st.markdown('**Comparar los modelos**  \nCurvas ROC, precisión-recall, ganancia, matrices de confusión e '
                'importancia de variables de cada algoritmo.')
    st.page_link('paginas/modelos.py', label='Ir a rendimiento', icon=':material/monitoring:')
with c.container(border=True):
    st.markdown('**Clasificar compradores**  \nBuscar un par usuario-vendedor, ingresar datos manualmente o '
                'subir un archivo, y ver la predicción de cada modelo.')
    st.page_link('paginas/prediccion.py', label='Ir a clasificación', icon=':material/person_search:')
