"""Aplicación del Proyecto 2 — Predicción de compradores recurrentes (Reto #11).

Ejecutar desde la raíz del repositorio:
    .venv/Scripts/python -m streamlit run app/app.py
"""
import streamlit as st

st.set_page_config(page_title='Compradores recurrentes · Tmall', page_icon=':material/storefront:',
                   layout='wide')

paginas = st.navigation([
    st.Page('paginas/inicio.py', title='Inicio', icon=':material/home:', default=True),
    st.Page('paginas/exploracion.py', title='Exploración de datos', icon=':material/query_stats:'),
    st.Page('paginas/modelos.py', title='Rendimiento de los modelos', icon=':material/monitoring:'),
    st.Page('paginas/prediccion.py', title='Clasificar compradores', icon=':material/person_search:'),
])

with st.sidebar:
    st.caption('**Reto #11** · Predicción de compradores recurrentes (Tianchi – Alibaba)  \n'
               'CC3084 Data Science · UVG · Semestre II 2026')

paginas.run()
