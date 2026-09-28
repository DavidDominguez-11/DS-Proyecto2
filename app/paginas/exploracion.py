import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import utils as u

MUESTRA_CORRELACION = 60_000


@st.cache_data
def resumen_variable(var):
    pares = u.cargar_pares()
    x, y = pares[var], pares['label']
    if x.nunique() <= 12:
        grupos = x.round(3).astype(str)
        orden = sorted(x.round(3).unique())
        etiquetas = [str(v) for v in orden]
    else:
        grupos = pd.qcut(x, 10, duplicates='drop')
        minimo = x.min()
        etiquetas = [f'{max(iv.left, minimo):.3g} – {iv.right:.3g}' for iv in grupos.cat.categories]
        grupos = grupos.cat.rename_categories(etiquetas)
    tramos = y.groupby(grupos, observed=True).agg(['mean', 'size']).reindex(etiquetas)
    medianas = x.groupby(y).median()
    return tramos, medianas


@st.cache_data
def histograma(var, log, recortar):
    pares = u.cargar_pares()
    x = pares[var].astype(float)
    if recortar:
        x = x.clip(upper=x.quantile(0.99))
    if log:
        x = np.log1p(x)
    bordes = np.histogram_bin_edges(x, bins=40)
    salida = {}
    for clase in (0, 1):
        conteo, _ = np.histogram(x[pares['label'] == clase], bins=bordes)
        salida[clase] = conteo / conteo.sum() * 100
    return bordes, salida


@st.cache_data
def caja(var):
    pares = u.cargar_pares()
    filas = {}
    for clase in (0, 1):
        x = pares.loc[pares['label'] == clase, var]
        q1, med, q3 = x.quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        filas[clase] = dict(q1=q1, median=med, q3=q3, lowerfence=max(x.min(), q1 - 1.5 * iqr),
                            upperfence=min(x.max(), q3 + 1.5 * iqr), mean=x.mean())
    return filas


@st.cache_data
def por_categoria(var):
    pares = u.cargar_pares()
    mapa = u.EDADES if var == 'age_range' else u.GENEROS
    t = pares.groupby(var)['label'].agg(['mean', 'size', 'sum'])
    t.index = [mapa[i] for i in t.index]
    return t


@st.cache_data
def correlacion(variables, metodo):
    pares = u.cargar_pares()
    muestra = pares.sample(min(MUESTRA_CORRELACION, len(pares)), random_state=42)
    return muestra[list(variables)].corr(method=metodo)


pares = u.cargar_pares()
dicc = u.cargar_diccionario()
dicc['nivel'] = dicc['variable'].map(u.nivel)
descripcion = dict(zip(dicc['variable'], dicc['descripcion']))

st.title('Exploración de los datos')
st.markdown(
    f'Tabla de modelado: **{len(pares):,} pares** usuario-vendedor etiquetados, con las **64 variables** que usan los '
    'modelos. Se construyeron a partir del registro de actividad después de la limpieza (edad y género '
    'recodificados, `50+` consolidado, desconocidos como categoría propia).')

tab_num, tab_cat, tab_corr, tab_dicc = st.tabs(
    [':material/bar_chart: Variables numéricas', ':material/groups: Edad y género',
     ':material/grid_on: Correlaciones', ':material/menu_book: Diccionario de variables'])

# --- Variables numéricas -----------------------------------------------------
with tab_num:
    niveles = ['Par usuario-vendedor', 'Usuario', 'Vendedor', 'Relación']
    nivel_sel = st.pills('Nivel de la variable', niveles, default='Par usuario-vendedor', key='nivel_num') or niveles[0]
    opciones = dicc[(dicc['nivel'] == nivel_sel)].sort_values('auc_abs', ascending=False)['variable'].tolist()
    var = st.selectbox('Variable (ordenadas por poder predictivo individual)', opciones,
                       format_func=lambda v: f'{v} — {descripcion[v]}')

    fila = dicc.set_index('variable').loc[var]
    tramos, medianas = resumen_variable(var)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric('AUC individual', f"{fila['auc_abs']:.3f}", border=True,
              help='Capacidad de la variable, por sí sola, de separar recurrentes de no recurrentes '
                   '(0.5 = nada; calculado en el conjunto de entrenamiento).')
    m2.metric('Relación con la recompra', 'Positiva' if fila['direccion'] == '+' else 'Negativa', border=True)
    m3.metric('Mediana — no recurrentes', f'{medianas.get(0, np.nan):,.3g}', border=True)
    m4.metric('Mediana — recurrentes', f'{medianas.get(1, np.nan):,.3g}', border=True)

    tasa_base = pares['label'].mean()
    fig = go.Figure(go.Bar(
        x=tramos.index.astype(str), y=tramos['mean'] * 100, marker_color=u.COLOR_PRIMARIO,
        customdata=tramos['size'],
        hovertemplate='%{x}<br>Tasa de recompra: %{y:.2f} %<br>Pares: %{customdata:,}<extra></extra>'))
    fig.add_hline(y=tasa_base * 100, line_dash='dot', line_color=u.COLOR_RECURRENTE,
                  annotation_text=f'Promedio {tasa_base:.1%}', annotation_position='top left')
    fig.update_layout(title=f'Tasa de recompra según {var}', xaxis_title=f'{var} (deciles o valores)',
                      yaxis_title='Tasa de recompra (%)', xaxis_type='category')
    st.plotly_chart(u.estilo(fig, 360), key='tramos')

    o1, o2 = st.columns(2)
    log = o1.toggle('Escala logarítmica (log(1 + x))', value=True, help='Útil porque casi todas las variables '
                    'tienen colas largas a la derecha.')
    recortar = o2.toggle('Recortar al percentil 99', value=True, help='Evita que unos pocos valores extremos '
                         'aplasten la gráfica. Los outliers se conservan en los modelos.')
    g1, g2 = st.columns([3, 2])
    with g1:
        bordes, hist = histograma(var, log, recortar)
        centros = (bordes[:-1] + bordes[1:]) / 2
        fig = go.Figure()
        for clase, color in [(0, u.COLOR_NO_RECURRENTE), (1, u.COLOR_RECURRENTE)]:
            fig.add_bar(x=centros, y=hist[clase], name=u.ETIQUETAS[clase], marker_color=color, opacity=0.7,
                        hovertemplate='%{x:.3g}: %{y:.1f} % de la clase<extra>' + u.ETIQUETAS[clase] + '</extra>')
        fig.update_layout(barmode='overlay', bargap=0, title='Distribución por clase (% dentro de cada clase)',
                          xaxis_title=f'log(1 + {var})' if log else var, yaxis_title='% de pares')
        st.plotly_chart(u.estilo(fig, 360), key='hist')
    with g2:
        stats = caja(var)
        fig = go.Figure()
        for clase, color in [(0, u.COLOR_NO_RECURRENTE), (1, u.COLOR_RECURRENTE)]:
            s = stats[clase]
            fig.add_trace(go.Box(name=u.ETIQUETAS[clase], x=[u.ETIQUETAS[clase]], q1=[s['q1']], median=[s['median']], q3=[s['q3']],
                                 lowerfence=[s['lowerfence']], upperfence=[s['upperfence']], mean=[s['mean']],
                                 marker_color=color, fillcolor=color, line_color='#33414E', opacity=0.8))
        fig.update_layout(title='Diagrama de caja (sin outliers)', yaxis_title=var, showlegend=False)
        st.plotly_chart(u.estilo(fig, 360), key='caja')
    st.caption('La línea punteada de la caja es la media. Los bigotes llegan hasta 1.5 veces el rango intercuartílico.')

# --- Edad y género -----------------------------------------------------------
with tab_cat:
    cat = st.segmented_control('Variable', ['Edad', 'Género'], default='Edad', key='cat') or 'Edad'
    var = 'age_range' if cat == 'Edad' else 'gender'
    t = por_categoria(var)
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(
            x=t.index, y=t['mean'] * 100, marker_color=u.COLOR_PRIMARIO, customdata=t['size'],
            text=[f'{v:.1%}' for v in t['mean']], textposition='outside',
            hovertemplate='%{x}<br>Tasa de recompra: %{y:.2f} %<br>Pares: %{customdata:,}<extra></extra>'))
        fig.add_hline(y=pares['label'].mean() * 100, line_dash='dot', line_color=u.COLOR_RECURRENTE)
        fig.update_layout(title=f'Tasa de recompra por {cat.lower()}', yaxis_title='Tasa de recompra (%)',
                          yaxis_range=[0, t['mean'].max() * 125])
        st.plotly_chart(u.estilo(fig, 380), key='cat_tasa')
    with c2:
        fig = go.Figure()
        fig.add_bar(x=t.index, y=t['size'] - t['sum'], name='No recurrente', marker_color=u.COLOR_NO_RECURRENTE)
        fig.add_bar(x=t.index, y=t['sum'], name='Recurrente', marker_color=u.COLOR_RECURRENTE)
        fig.update_layout(barmode='stack', title=f'Pares por {cat.lower()} y tipo de comprador', yaxis_title='Pares')
        st.plotly_chart(u.estilo(fig, 380), key='cat_conteo')
    st.caption('Las diferencias demográficas son de 1–2 puntos porcentuales (V de Cramér ≈ 0.02): la edad y el género '
               'aportan poca información a los modelos. El grupo `<18` tiene solo 13 pares.')

# --- Correlaciones -----------------------------------------------------------
with tab_corr:
    todas = dicc.sort_values('auc_abs', ascending=False)['variable'].tolist()
    c1, c2 = st.columns([3, 1])
    variables = c1.multiselect('Variables (por defecto, las 12 con mayor AUC individual)', todas, default=todas[:12])
    metodo = c2.segmented_control('Método', ['Spearman', 'Pearson'], default='Spearman', key='metodo') or 'Spearman'
    incluir_label = c2.toggle('Incluir la etiqueta', value=True)
    if len(variables) < 2:
        st.info('Elige al menos dos variables.')
    else:
        cols = tuple(variables + (['label'] if incluir_label else []))
        corr = correlacion(cols, metodo.lower())
        fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r', zmin=-1, zmax=1, aspect='auto')
        fig.update_layout(title=f'Correlación de {metodo} (muestra de {MUESTRA_CORRELACION:,} pares)')
        st.plotly_chart(u.estilo(fig, 120 + 32 * len(cols), leyenda_arriba=False), key='corr')
        st.caption('Spearman es robusta a los outliers y a las distribuciones sesgadas. Las correlaciones con la '
                   'etiqueta son débiles (≤ 0.10): los modelos necesitan combinar muchas variables.')

# --- Diccionario -------------------------------------------------------------
with tab_dicc:
    c1, c2 = st.columns([2, 1])
    filtro_nivel = c1.pills('Nivel', ['Par usuario-vendedor', 'Usuario', 'Vendedor', 'Relación', 'Demográfica'],
                            selection_mode='multi', default=[], key='dicc_nivel')
    buscar = c2.text_input('Buscar', placeholder='p. ej. compras, días, fidelidad')
    vista = dicc.copy()
    if filtro_nivel:
        vista = vista[vista['nivel'].isin(filtro_nivel)]
    if buscar:
        patron = buscar.lower()
        vista = vista[vista['variable'].str.lower().str.contains(patron, regex=False)
                      | vista['descripcion'].str.lower().str.contains(patron, regex=False)]
    st.dataframe(
        vista[['variable', 'nivel', 'descripcion', 'auc_abs', 'direccion']].sort_values('auc_abs', ascending=False),
        hide_index=True,
        column_config={
            'variable': 'Variable', 'nivel': 'Nivel', 'descripcion': st.column_config.TextColumn('Descripción', width='large'),
            'auc_abs': st.column_config.ProgressColumn('AUC individual', min_value=0.5, max_value=0.65, format='%.3f'),
            'direccion': st.column_config.TextColumn('Relación', help='+ la recompra aumenta con la variable; − disminuye'),
        })
    with st.expander('Ver una muestra de la tabla de modelado'):
        st.dataframe(pares.drop(columns=['cv_fold']).head(200), hide_index=True)
