import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import utils as u

VARIABLES_CLAVE = [
    ('m_repeat_buyer_rate_log', 'Fidelidad histórica de la clientela del vendedor'),
    ('p_n_items', 'Productos distintos del vendedor que exploró'),
    ('p_purchase', 'Compras al vendedor el 11/11'),
    ('p_n_cats', 'Categorías distintas exploradas'),
    ('p_first_days_before', 'Días desde su primera interacción con el vendedor'),
    ('p_n_days', 'Días con actividad con el vendedor'),
    ('u_n_days', 'Días activos del usuario en la plataforma'),
    ('u_n_merchants', 'Vendedores con los que interactuó el usuario'),
]


@st.cache_data
def referencia_variables():
    """Percentiles y medianas por clase de las variables clave en los pares etiquetados."""
    pares = u.cargar_pares()
    cols = [v for v, _ in VARIABLES_CLAVE]
    return {v: np.sort(pares[v].to_numpy()) for v in cols}, pares.groupby('label')[cols].median()


@st.cache_data
def pares_disponibles():
    """Todos los pares con variables calculadas, indicando de qué conjunto provienen."""
    etiquetados = u.cargar_pares()
    etiquetados = etiquetados.assign(origen=etiquetados['split'].map({'train': 'entrenamiento', 'test': 'prueba'}))
    competencia = u.cargar_competencia().assign(origen='competencia')
    return pd.concat([competencia, etiquetados.drop(columns=['split', 'cv_fold', 'label'])], ignore_index=True)


def elegir_modelos():
    sel = st.pills('Modelos a usar', u.MODELOS, selection_mode='multi', default=u.MODELOS, key='pred_modelos',
                   help='Puedes clasificar con un solo modelo o con todos a la vez.')
    return [m for m in u.MODELOS if m in (sel or [])]


def tarjeta(modelo, puntaje):
    percentil, tasa_decil, decil = u.interpretar(modelo, puntaje)
    umbral = u.umbral(modelo)
    recurrente = puntaje >= umbral
    with st.container(border=True):
        st.markdown(f"<span style='color:{u.COLORES_MODELO[modelo]}; font-weight:700'>● {modelo}</span>",
                    unsafe_allow_html=True)
        if recurrente:
            st.markdown(f"<span style='background:{u.COLOR_RECURRENTE}; color:white; padding:3px 10px; "
                        "border-radius:12px; font-weight:600'>Recurrente probable</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='background:{u.COLOR_NO_RECURRENTE}; color:white; padding:3px 10px; "
                        "border-radius:12px; font-weight:600'>No recurrente probable</span>", unsafe_allow_html=True)
        st.metric('Percentil del puntaje', f'{percentil[0]:.0%}',
                  help='Porcentaje de los compradores de prueba con un puntaje menor o igual.')
        st.caption(f'Puntaje {puntaje:.3f} (umbral {umbral:.3f}). En el decil {decil[0]} de puntaje, '
                   f'el **{tasa_decil[0]:.1%}** de los compradores de prueba volvió a comprar.')


def mostrar_resultados(X, modelos, clave, etiqueta_real=None):
    if not modelos:
        st.info('Selecciona al menos un modelo.')
        return
    puntajes = u.predecir(X)
    st.subheader('Resultado')
    if etiqueta_real is not None:
        texto = 'volvió a comprar' if etiqueta_real == 1 else 'no volvió a comprar'
        st.info(f'**Respuesta real** (par del conjunto de prueba): este comprador **{texto}** al vendedor.',
                icon=':material/fact_check:')
    cols = st.columns(len(modelos))
    for col, m in zip(cols, modelos):
        with col:
            tarjeta(m, float(puntajes[m][0]))

    fig = go.Figure()
    for m in modelos:
        percentil = u.interpretar(m, puntajes[m])[0][0] * 100
        fig.add_bar(y=[m], x=[percentil], orientation='h', marker_color=u.COLORES_MODELO[m], showlegend=False,
                    text=[f'{percentil:.0f}'], textposition='outside',
                    hovertemplate=f'{m}: percentil %{{x:.1f}}<extra></extra>')
        corte = u.percentil_umbral(m) * 100
        fig.add_scatter(x=[corte, corte], y=[m, m], mode='markers', showlegend=False,
                        marker=dict(symbol='line-ns', size=28, line=dict(width=3, color='#1E2A35')),
                        hovertemplate=f'Umbral de {m}: percentil {corte:.1f}<extra></extra>')
    fig.update_layout(title='Posición del comprador entre los compradores de prueba (la marca negra es el umbral)',
                      xaxis=dict(range=[0, 105], title='Percentil del puntaje'), yaxis_autorange='reversed')
    st.plotly_chart(u.estilo(fig, 90 + 55 * len(modelos), leyenda_arriba=False), key=f'barras_{clave}')

    with st.expander('¿Por qué este resultado? — comparación con los demás compradores', expanded=True):
        ordenados, medianas = referencia_variables()
        filas = []
        for v, nombre in VARIABLES_CLAVE:
            valor = float(X[v].iloc[0])
            filas.append({'Variable': nombre, 'Código': v, 'Valor del comprador': valor,
                          'Percentil': 100 * np.searchsorted(ordenados[v], valor, side='right') / len(ordenados[v]),
                          'Mediana no recurrentes': medianas.loc[0, v], 'Mediana recurrentes': medianas.loc[1, v]})
        vendedores = u.cargar_vendedores()
        mid = int(X['merchant_id'].iloc[0])
        if mid in vendedores.index and pd.notna(vendedores.loc[mid, 'tasa_recompra_train']):
            st.markdown(f"**Vendedor {mid}**: en el entrenamiento, el **{vendedores.loc[mid, 'tasa_recompra_train']:.1%}** "
                        f"de sus {vendedores.loc[mid, 'pares_train']:,} compradores nuevos volvió a comprar "
                        f"(promedio general {u.cargar_pares()['label'].mean():.1%}). Es la variable más importante de "
                        'los tres modelos.')
        tabla = pd.DataFrame(filas).set_index('Variable')
        for col in ['Valor del comprador', 'Mediana no recurrentes', 'Mediana recurrentes']:
            tabla[col] = tabla[col].map(lambda v: f'{v:,.3g}')
        tabla['Percentil'] = tabla['Percentil'].map(lambda v: f'{v:.0f} %')
        st.table(tabla)
        st.caption('Se muestran las variables más importantes según los modelos. Percentil = posición del comprador '
                   'entre los 260,864 pares etiquetados.')


st.title('Clasificar compradores')
st.markdown('Estima si un comprador nuevo del Double 11 volverá a comprar al vendedor. El preprocesamiento '
            '(construcción de las 64 variables, transformaciones y codificación del vendedor) ocurre '
            'automáticamente con el mismo `Pipeline` usado en el entrenamiento.')
with st.expander('¿Cómo interpretar el resultado?'):
    st.markdown(
        '- **Clase**: *recurrente probable* si el puntaje supera el umbral del modelo (el que maximizó F1 en el '
        'entrenamiento). Con ese umbral, ~15 % de los marcados como recurrentes realmente vuelven, 2.5 veces la tasa '
        'base, y se detecta ~32–36 % de los recurrentes.\n'
        '- **Percentil**: posición del comprador entre los 52,173 compradores de prueba. Es comparable entre modelos.\n'
        '- **Tasa en su decil**: de los compradores de prueba con un puntaje parecido, qué porcentaje volvió realmente. '
        'Es la mejor lectura de "probabilidad".\n'
        '- **El puntaje crudo no es una probabilidad**: la Regresión Logística y Random Forest usan pesos de clase '
        'balanceados, que lo desplazan hacia arriba.')

modelos = elegir_modelos()
PESTANAS = {'buscar': ':material/search: Buscar un par',
            'manual': ':material/edit_note: Ingresar datos manualmente',
            'archivo': ':material/upload_file: Clasificar un archivo'}
# ?pestana=manual en la URL abre directamente esa pestaña (útil para demostraciones)
pestana_inicial = PESTANAS.get(st.query_params.get('pestana', 'buscar'), PESTANAS['buscar'])
tab_buscar, tab_manual, tab_archivo = st.tabs(list(PESTANAS.values()), default=pestana_inicial)

# --- Buscar un par -----------------------------------------------------------
with tab_buscar:
    origen = st.segmented_control(
        'Origen', ['Prueba (con respuesta conocida)', 'Competencia (sin respuesta)'],
        default='Prueba (con respuesta conocida)', key='origen',
        help='Prueba: pares reservados para evaluar, cuya respuesta real conocemos. Competencia: pares del archivo '
             'de prueba oficial, sin etiqueta: datos realmente nuevos.') or 'Prueba (con respuesta conocida)'
    con_respuesta = origen.startswith('Prueba')
    if con_respuesta:
        pares = u.cargar_pares()
        datos = pares[pares['split'] == 'test']
    else:
        datos = u.cargar_competencia()

    clave_usuario = f'usuario_{con_respuesta}'
    c1, c2, c3 = st.columns([1, 1, 1], vertical_alignment='bottom')
    if c3.button('Elegir un par al azar', icon=':material/casino:', width='stretch'):
        fila = datos.sample(1).iloc[0]
        st.session_state[clave_usuario] = int(fila['user_id'])
        st.session_state[f'vendedor_{con_respuesta}'] = int(fila['merchant_id'])
    if clave_usuario not in st.session_state:
        st.session_state[clave_usuario] = int(datos['user_id'].iloc[0])
    user_id = c1.number_input('user_id', min_value=1, step=1, key=clave_usuario)
    del_usuario = datos[datos['user_id'] == user_id]
    if del_usuario.empty:
        st.warning(f'El usuario {user_id} no tiene pares en este conjunto. Prueba con "Elegir un par al azar".')
    else:
        vendedores_usuario = del_usuario['merchant_id'].astype(int).tolist()
        clave_vendedor = f'vendedor_{con_respuesta}'
        if st.session_state.get(clave_vendedor) not in vendedores_usuario:
            st.session_state[clave_vendedor] = vendedores_usuario[0]
        merchant_id = c2.selectbox('merchant_id', vendedores_usuario, key=clave_vendedor)
        fila = del_usuario[del_usuario['merchant_id'] == merchant_id]
        r = fila.iloc[0]
        st.caption(f"Usuario {user_id} · edad {u.EDADES[int(r['age_range'])]} · género {u.GENEROS[int(r['gender'])]} · "
                   f"{int(r['p_actions'])} interacciones con el vendedor ({int(r['p_actions_pre'])} antes del 11/11) · "
                   f"{int(r['p_n_items'])} productos explorados · {int(r['p_purchase'])} compras el 11/11")
        mostrar_resultados(fila, modelos, 'buscar', int(r['label']) if con_respuesta else None)

# --- Ingreso manual ----------------------------------------------------------
with tab_manual:
    vendedores = u.cargar_vendedores()
    perfiles = u.cargar_perfiles()
    conocidos = vendedores[vendedores['pares_train'] > 0].sort_values('pares_train', ascending=False)
    st.markdown('Describe la relación de un comprador con un vendedor. Solo se piden los datos principales; el resto '
                'de las 64 variables se completa con el perfil real del vendedor elegido y de un usuario típico con el '
                'nivel de actividad indicado.')
    with st.form('manual'):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('**Vendedor y comprador**')
            merchant_id = st.selectbox(
                'Vendedor (ordenados por número de compradores)', conocidos.index.tolist(),
                format_func=lambda m: f"{m} — tasa histórica de recompra {conocidos.loc[m, 'tasa_recompra_train']:.1%}")
            edad = st.selectbox('Rango de edad', list(u.EDADES), index=4, format_func=u.EDADES.get)
            genero = st.selectbox('Género', list(u.GENEROS), format_func=u.GENEROS.get)
            perfil = st.select_slider('Actividad general del usuario en la plataforma', perfiles.index.tolist(),
                                      value='Media', help='Baja/Media/Alta/Muy alta = percentil 25/50/75/90 de '
                                                          'interacciones totales entre los usuarios de entrenamiento.')
        with c2:
            st.markdown('**Antes del Double 11** (con este vendedor)')
            a1, a2, a3 = st.columns(3)
            clics_pre = a1.number_input('Clics', 0, 5000, 0, key='clics_pre')
            favoritos_pre = a2.number_input('Favoritos', 0, 500, 0, key='favoritos_pre')
            carrito_pre = a3.number_input('Carrito', 0, 100, 0, key='carrito_pre')
            b1, b2, b3 = st.columns(3)
            dias_pre = b1.number_input('Días con actividad', 0, 180, 0)
            primera = b2.number_input('Días desde la 1.ª visita', 0, 184, 0, help='Días entre la primera interacción '
                                      'con el vendedor y el 11/11.')
            ultima = b3.number_input('Días desde la última', 0, 184, 0, help='Días entre la última interacción previa '
                                     'y el 11/11.')
        st.markdown('**El 11 de noviembre** (con este vendedor)')
        d1, d2, d3, d4 = st.columns(4)
        clics_d11 = d1.number_input('Clics', 0, 5000, 4, key='clics_d11')
        favoritos_d11 = d2.number_input('Favoritos', 0, 500, 0, key='favoritos_d11')
        carrito_d11 = d3.number_input('Carrito', 0, 100, 0, key='carrito_d11')
        compras = d4.number_input('Compras', 1, 20, 1, help='Todos los pares tienen al menos una compra el 11/11.')
        e1, e2, e3, e4 = st.columns(4)
        productos = e1.number_input('Productos distintos explorados (en total)', 1, 1000, 2)
        productos_comprados = e2.number_input('Productos distintos comprados', 1, 20, 1)
        categorias = e3.number_input('Categorías distintas', 1, 100, 1)
        marcas = e4.number_input('Marcas distintas', 0, 50, 1)
        enviado = st.form_submit_button('Clasificar', type='primary', icon=':material/play_arrow:')

    if enviado:
        avisos = []
        hay_previa = clics_pre + favoritos_pre + carrito_pre > 0
        if hay_previa:
            if dias_pre == 0:
                dias_pre = 1
                avisos.append('Hubo actividad previa, así que los días con actividad previa se ajustaron a 1.')
            if primera == 0:
                primera = max(ultima, 1)
                avisos.append('Los días desde la primera visita se ajustaron para ser al menos 1.')
            if ultima == 0 or ultima > primera:
                ultima = min(max(ultima, 1), primera)
                avisos.append('Los días desde la última visita se ajustaron para no superar a los de la primera.')
            if dias_pre > primera:
                dias_pre = primera
                avisos.append('Los días con actividad previa no pueden superar los días desde la primera visita.')
        elif dias_pre or primera or ultima:
            avisos.append('Sin clics, favoritos ni carrito previos, los días de actividad previa se toman como 0.')
        if productos_comprados > compras:
            productos_comprados = compras
            avisos.append('Los productos comprados no pueden superar el número de compras.')
        if productos < productos_comprados:
            productos = productos_comprados
            avisos.append('Los productos explorados se ajustaron para incluir los comprados.')
        if categorias > productos:
            categorias = productos
            avisos.append('Las categorías no pueden superar a los productos explorados.')
        for aviso in avisos:
            st.warning(aviso, icon=':material/info:')
        entrada = dict(merchant_id=merchant_id, edad=edad, genero=genero, clics_pre=clics_pre,
                       favoritos_pre=favoritos_pre, carrito_pre=carrito_pre, dias_pre=dias_pre,
                       primera_interaccion=primera, ultima_interaccion=ultima, clics_d11=clics_d11,
                       favoritos_d11=favoritos_d11, carrito_d11=carrito_d11, compras=compras, productos=productos,
                       productos_comprados=productos_comprados, categorias=categorias, marcas=marcas)
        X = u.construir_fila_manual(entrada, vendedores.loc[merchant_id], perfiles.loc[perfil])
        mostrar_resultados(X, modelos, 'manual')
        with st.expander('Ver las 64 variables construidas para el modelo'):
            st.dataframe(X.T.rename(columns={0: 'valor'}))

# --- Archivo -----------------------------------------------------------------
with tab_archivo:
    st.markdown('Sube un archivo CSV con las columnas `user_id` y `merchant_id` (por ejemplo, filas de '
                '`test_format1.csv`). La aplicación busca las variables de cada par y lo clasifica con los modelos '
                'elegidos.')
    ejemplo = u.cargar_competencia()[['user_id', 'merchant_id']].sample(20, random_state=1)
    st.download_button('Descargar un archivo de ejemplo', ejemplo.to_csv(index=False), 'pares_ejemplo.csv',
                       'text/csv', icon=':material/download:')
    archivo = st.file_uploader('Archivo CSV', type='csv')
    if archivo is not None:
        try:
            entrada = pd.read_csv(archivo)
        except Exception as error:  # archivo mal formado
            st.error(f'No se pudo leer el archivo: {error}')
            st.stop()
        faltan = {'user_id', 'merchant_id'} - set(entrada.columns)
        if faltan:
            st.error(f'Faltan columnas: {", ".join(sorted(faltan))}')
        elif not modelos:
            st.info('Selecciona al menos un modelo.')
        else:
            entrada = entrada[['user_id', 'merchant_id']].dropna().astype(int).drop_duplicates()
            encontrados = entrada.merge(pares_disponibles(), on=['user_id', 'merchant_id'], how='inner')
            no_encontrados = len(entrada) - len(encontrados)
            st.write(f'Pares leídos: **{len(entrada):,}** · encontrados: **{len(encontrados):,}** · '
                     f'no encontrados: **{no_encontrados:,}**')
            if no_encontrados:
                st.caption('Solo se pueden clasificar pares que existen en los datos del reto (entrenamiento o '
                           'prueba de la competencia), porque sus variables se calculan a partir del registro de actividad.')
            if len(encontrados):
                puntajes = u.predecir(encontrados)
                salida = encontrados[['user_id', 'merchant_id', 'origen']].copy()
                for m in modelos:
                    clave = u.CLAVE_MODELO[m]
                    salida[f'percentil_{clave}'] = 100 * u.interpretar(m, puntajes[m])[0]
                    salida[f'recurrente_{clave}'] = puntajes[m] >= u.umbral(m)
                salida['modelos_que_predicen_recurrente'] = salida[[c for c in salida if c.startswith('recurrente_')]].sum(axis=1)
                salida = salida.sort_values(f'percentil_{u.CLAVE_MODELO[modelos[0]]}', ascending=False)
                if (salida['origen'] == 'entrenamiento').any():
                    st.warning('Algunos pares pertenecen al conjunto de entrenamiento: los modelos ya los vieron, así que '
                               'su predicción es optimista.', icon=':material/warning:')
                st.dataframe(salida, hide_index=True, column_config={
                    c: st.column_config.ProgressColumn(c, min_value=0, max_value=100, format='%.0f %%')
                    for c in salida if c.startswith('percentil_')})
                st.download_button('Descargar resultados', salida.to_csv(index=False), 'clasificacion.csv', 'text/csv',
                                   icon=':material/download:', type='primary')
