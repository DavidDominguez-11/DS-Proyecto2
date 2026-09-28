"""Genera los datos compactos que usa la aplicación (carpeta app/data).

Requiere haber ejecutado notebooks/02_ingenieria_variables.ipynb, que produce
data/processed/features_train.parquet y data/processed/features_test.parquet.

Uso (desde la raíz del repositorio):
    .venv/Scripts/python app/preparar_datos.py
"""
from pathlib import Path

import pandas as pd

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
PROCESSED_DIR = ROOT_DIR / 'data' / 'processed'
DATA_DIR = APP_DIR / 'data'

# Percentil de actividad del usuario que representa cada perfil del formulario manual
PERFILES = {'Baja': 0.25, 'Media': 0.50, 'Alta': 0.75, 'Muy alta': 0.90}


def main():
    DATA_DIR.mkdir(exist_ok=True)
    etiquetados = pd.read_parquet(PROCESSED_DIR / 'features_train.parquet')
    competencia = pd.read_parquet(PROCESSED_DIR / 'features_test.parquet')

    # 1. Pares etiquetados (con split y pliegue) y pares de la competencia (sin etiqueta)
    etiquetados.to_parquet(DATA_DIR / 'pares_etiquetados.parquet', index=False, compression='zstd')
    competencia.to_parquet(DATA_DIR / 'pares_competencia.parquet', index=False, compression='zstd')

    # 2. Perfil de cada vendedor: variables m_ (no dependen del par) y su tasa de recompra
    #    calculada solo con el conjunto de entrenamiento (la misma información que ve el modelo)
    cols_m = [c for c in etiquetados.columns if c.startswith('m_')]
    vendedores = (
        pd.concat([etiquetados[['merchant_id'] + cols_m], competencia[['merchant_id'] + cols_m]])
        .drop_duplicates('merchant_id').set_index('merchant_id').sort_index()
    )
    entrenamiento = etiquetados[etiquetados['split'] == 'train']
    tasa = entrenamiento.groupby('merchant_id')['label'].agg(tasa_recompra_train='mean', pares_train='size')
    vendedores = vendedores.join(tasa)
    vendedores['pares_train'] = vendedores['pares_train'].fillna(0).astype(int)
    vendedores.to_parquet(DATA_DIR / 'vendedores.parquet', compression='zstd')

    # 3. Perfiles de usuario reales para el formulario manual: el usuario de entrenamiento
    #    ubicado en el percentil indicado de actividad total (u_actions)
    cols_u = [c for c in etiquetados.columns if c.startswith('u_')]
    usuarios = entrenamiento.drop_duplicates('user_id').sort_values(['u_actions', 'user_id']).reset_index(drop=True)
    filas = []
    for nombre, q in PERFILES.items():
        fila = usuarios.loc[int(q * (len(usuarios) - 1)), cols_u].copy()
        fila['perfil'] = nombre
        fila['percentil'] = q
        filas.append(fila)
    perfiles = pd.DataFrame(filas).set_index('perfil')
    perfiles.to_parquet(DATA_DIR / 'perfiles_usuario.parquet', compression='zstd')

    for f in sorted(DATA_DIR.glob('*.parquet')):
        print(f'{f.name:<28} {f.stat().st_size / 1e6:6.1f} MB')


if __name__ == '__main__':
    main()
