"""Utilidades compartidas por las páginas de la aplicación: rutas, paleta, carga y predicción."""
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
DATA_DIR = APP_DIR / 'data'
MODEL_DIR = ROOT_DIR / 'outputs' / 'models'
TABLE_DIR = ROOT_DIR / 'outputs' / 'tables'

# --- Paleta ------------------------------------------------------------------
# Azul (confianza, color principal) y su complementario naranja para resaltar la clase
# de interés (recurrente); gris azulado neutro para la clase mayoritaria y referencias.
# Los modelos usan la paleta Okabe-Ito (distinguible con daltonismo), igual que las
# figuras estáticas de los notebooks.
COLOR_PRIMARIO = '#1F5F8B'
COLOR_RECURRENTE = '#E07A1F'
COLOR_NO_RECURRENTE = '#8C9BAB'
COLOR_REFERENCIA = '#6B7785'
COLORES_MODELO = {
    'Regresión Logística': '#0072B2',
    'Random Forest': '#009E73',
    'LightGBM': '#D55E00',
    'Ensamble': '#CC79A7',
}
MODELOS = list(COLORES_MODELO)
MODELOS_BASE = MODELOS[:3]
MODELO_PRINCIPAL = 'LightGBM'
CLAVE_MODELO = {'Regresión Logística': 'lr', 'Random Forest': 'rf', 'LightGBM': 'lgbm', 'Ensamble': 'ens'}

NIVELES = {'p': 'Par usuario-vendedor', 'u': 'Usuario', 'm': 'Vendedor', 'x': 'Relación'}
EDADES = {0: 'Desconocido', 1: '<18', 2: '18-24', 3: '25-29', 4: '30-34', 5: '35-39', 6: '40-49', 7: '50+'}
GENEROS = {0: 'Femenino', 1: 'Masculino', 2: 'Desconocido'}
ETIQUETAS = {0: 'No recurrente', 1: 'Recurrente'}


def nivel(variable):
    return NIVELES.get(variable.split('_')[0], 'Demográfica')


def estilo(fig, alto=380, leyenda_arriba=True):
    """Formato común para las gráficas de Plotly."""
    tiene_titulo = bool(fig.layout.title.text)
    # Con título y leyenda arriba se reserva más margen para que no se encimen
    margen_superior = 50 + (45 if tiene_titulo and leyenda_arriba else 0)
    fig.update_layout(
        height=alto, margin=dict(l=10, r=10, t=margen_superior, b=10),
        font=dict(size=13), hoverlabel=dict(font_size=13),
        title=dict(y=0.98, yanchor='top') if tiene_titulo else None,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0) if leyenda_arriba else None,
    )
    return fig


# --- Carga de datos (en caché) -----------------------------------------------
@st.cache_data(show_spinner='Cargando pares etiquetados…')
def cargar_pares():
    return pd.read_parquet(DATA_DIR / 'pares_etiquetados.parquet')


@st.cache_data(show_spinner='Cargando pares de la competencia…')
def cargar_competencia():
    return pd.read_parquet(DATA_DIR / 'pares_competencia.parquet')


@st.cache_data
def cargar_vendedores():
    return pd.read_parquet(DATA_DIR / 'vendedores.parquet')


@st.cache_data
def cargar_perfiles():
    return pd.read_parquet(DATA_DIR / 'perfiles_usuario.parquet')


@st.cache_data
def cargar_tabla(nombre, **kwargs):
    return pd.read_csv(TABLE_DIR / nombre, **kwargs)


@st.cache_data
def cargar_diccionario():
    return cargar_tabla('diccionario_variables.csv')


@st.cache_resource(show_spinner='Cargando modelos…')
def cargar_modelos():
    metadata = json.loads((MODEL_DIR / 'metadata.json').read_text(encoding='utf-8'))
    pipelines = {m: joblib.load(MODEL_DIR / metadata['modelos'][m]['archivo']) for m in MODELOS_BASE}
    ref = np.load(MODEL_DIR / 'referencia_ensamble.npz')
    referencia = {m: ref[CLAVE_MODELO[m]] for m in MODELOS_BASE}
    return metadata, pipelines, referencia


@st.cache_data
def cargar_predicciones_prueba():
    return pd.read_parquet(MODEL_DIR / 'predicciones_prueba.parquet')


def metricas_prueba(modelo):
    return cargar_modelos()[0]['modelos'][modelo]['metricas_prueba']


def umbral(modelo):
    return cargar_modelos()[0]['modelos'][modelo]['umbral']


# --- Predicción --------------------------------------------------------------
def predecir(X):
    """Puntaje de cada modelo para las filas de X (mismo preprocesamiento que en el entrenamiento)."""
    metadata, pipelines, referencia = cargar_modelos()
    X = X[metadata['features']]
    puntajes = {m: pipelines[m].predict_proba(X)[:, 1] for m in MODELOS_BASE}
    # Ensamble: promedio del percentil de cada modelo en su distribución fuera de pliegue
    puntajes['Ensamble'] = np.mean(
        [np.searchsorted(referencia[m], puntajes[m], side='right') / len(referencia[m]) for m in MODELOS_BASE],
        axis=0)
    return puntajes


@st.cache_data
def _referencia_prueba():
    """Puntajes ordenados y tasa de recompra por decil de puntaje en el conjunto de prueba."""
    pred = cargar_predicciones_prueba()
    salida = {}
    for m in MODELOS:
        p = pred[f'p_{CLAVE_MODELO[m]}'].to_numpy()
        cortes = np.quantile(p, np.linspace(0, 1, 11))[1:-1]
        decil = np.searchsorted(cortes, p, side='right')
        tasa = pd.Series(pred['label'].to_numpy()).groupby(decil).mean().reindex(range(10)).to_numpy()
        salida[m] = {'ordenados': np.sort(p), 'cortes': cortes, 'tasa_decil': tasa}
    return salida


def interpretar(modelo, puntajes):
    """Percentil del puntaje entre los pares de prueba y tasa real de recompra en su decil."""
    ref = _referencia_prueba()[modelo]
    puntajes = np.atleast_1d(puntajes)
    percentil = np.searchsorted(ref['ordenados'], puntajes, side='right') / len(ref['ordenados'])
    decil = np.searchsorted(ref['cortes'], puntajes, side='right')
    return percentil, ref['tasa_decil'][decil], decil + 1


def percentil_umbral(modelo):
    ref = _referencia_prueba()[modelo]['ordenados']
    return np.searchsorted(ref, umbral(modelo), side='left') / len(ref)


# --- Construcción de una fila a partir del formulario manual ------------------
def construir_fila_manual(entrada, vendedor, perfil_usuario):
    """Arma las 64 variables de un par a partir de pocos datos, sin que el usuario transforme nada.

    - Variables del par (p_): se derivan de los conteos ingresados.
    - Variables del vendedor (m_): perfil real del vendedor elegido.
    - Variables del usuario (u_): perfil real de un usuario con el nivel de actividad elegido,
      ajustado para que sea coherente con la actividad del par (el total del usuario no puede
      ser menor que lo que hizo con este vendedor).
    """
    e = entrada
    f = {}
    f['p_clicks_pre'], f['p_cart_pre'], f['p_favorite_pre'] = e['clics_pre'], e['carrito_pre'], e['favoritos_pre']
    f['p_actions_pre'] = e['clics_pre'] + e['carrito_pre'] + e['favoritos_pre']
    f['p_actions_d11'] = e['clics_d11'] + e['carrito_d11'] + e['favoritos_d11'] + e['compras']
    f['p_clicks'] = e['clics_pre'] + e['clics_d11']
    f['p_cart'] = e['carrito_pre'] + e['carrito_d11']
    f['p_favorite'] = e['favoritos_pre'] + e['favoritos_d11']
    f['p_purchase'] = e['compras']
    f['p_actions'] = f['p_actions_pre'] + f['p_actions_d11']
    f['p_n_items'], f['p_n_items_bought'] = e['productos'], e['productos_comprados']
    f['p_n_cats'], f['p_n_brands'] = e['categorias'], e['marcas']
    f['p_has_pre'] = int(f['p_actions_pre'] > 0)
    f['p_n_days_pre'] = e['dias_pre'] if f['p_has_pre'] else 0
    f['p_n_days'] = f['p_n_days_pre'] + 1
    f['p_first_days_before'] = e['primera_interaccion'] if f['p_has_pre'] else 0
    f['p_last_pre_days_before'] = e['ultima_interaccion'] if f['p_has_pre'] else 0
    for tipo, col in [('click', 'p_clicks'), ('cart', 'p_cart'), ('purchase', 'p_purchase'),
                      ('favorite', 'p_favorite')]:
        f[f'p_{tipo}_rate'] = f[col] / f['p_actions']
    f['p_d11_share'] = f['p_actions_d11'] / f['p_actions']

    u = perfil_usuario.to_dict()
    minimos = {'u_actions': 'p_actions', 'u_clicks': 'p_clicks', 'u_cart': 'p_cart', 'u_purchase': 'p_purchase',
               'u_favorite': 'p_favorite', 'u_actions_d11': 'p_actions_d11', 'u_n_items': 'p_n_items',
               'u_n_cats': 'p_n_cats', 'u_n_brands': 'p_n_brands', 'u_n_days': 'p_n_days'}
    for col_u, col_p in minimos.items():
        u[col_u] = max(u[col_u], f[col_p])
    u['u_actions'] = max(u['u_actions'], u['u_clicks'] + u['u_cart'] + u['u_purchase'] + u['u_favorite'])
    for col in ['u_n_merchants', 'u_n_merchants_bought', 'u_n_merchants_bought_d11', 'u_n_days_purchase']:
        u[col] = max(u[col], 1)
    u['u_purchase_rate'] = u['u_purchase'] / u['u_actions']
    u['u_d11_share'] = u['u_actions_d11'] / u['u_actions']
    u['u_repeat_share'] = u['u_n_merchants_repeat'] / u['u_n_merchants_bought']
    f.update({k: v for k, v in u.items() if k.startswith('u_')})

    f.update({k: v for k, v in vendedor.items() if k.startswith('m_')})
    f['x_share_user_actions'] = f['p_actions'] / f['u_actions']
    f['x_share_user_purchase'] = f['p_purchase'] / f['u_purchase']
    f['x_share_user_merchants_d11'] = 1 / f['u_n_merchants_bought_d11']
    f['age_range'], f['gender'] = e['edad'], e['genero']
    f['merchant_id'] = e['merchant_id']

    features = cargar_modelos()[0]['features']
    faltan = set(features) - set(f)
    assert not faltan, f'Faltan variables: {faltan}'
    return pd.DataFrame([f])[features]
