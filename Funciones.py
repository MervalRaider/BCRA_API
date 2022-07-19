import numpy as np
import pandas as pd
import datetime as dt
import requests, json
import os



def data_2_col(url):
    '''#Función para organizar en un DataFrame la data recibida, con nombres de columnas definidos
    Para crear un token de acceso a la API del BCRA: https://estadisticasbcra.com/api/documentacion'''
    headers = {
        'Authorization':
            os.environ.get('BCRA-API2')}
    a = requests.get(url, headers=headers)
    b = json.loads(a.text)
    b = pd.DataFrame(b)
    b.columns = ['Fecha', 'Valor']
    b['Fecha'] = pd.to_datetime(b['Fecha'])
    b.set_index('Fecha', inplace=True)

    return b


#Función para extraer el valor del dólar blue de ambito
def dolar_blue(desde, hasta):
    url = "https://mercados.ambito.com//dolar/informal/historico-general/"

    inicio = desde.split(sep='-')
    inicio = dt.datetime(int(inicio[0]), int(inicio[1]), int(inicio[2]))
    final = hasta.split(sep='-')
    final = dt.datetime(int(final[0]), int(final[1]), int(final[2]))
    final = final.strftime('%d/%m/%Y')
    inicio = inicio.strftime('%d/%m/%Y')
    inicio = inicio.replace('/', '-')
    final = final.replace('/', '-')

    req = requests.get(url + inicio + '/' + final)

    data = req.json()
    data2 = np.array(data)
    df1 = pd.DataFrame(data2, columns=['Fecha', 'Compra', 'Venta'])
    df = df1.drop(labels=0, axis=0)
    df['Compra'] = df['Compra'].str.replace(",", ".").astype(float)
    df['Venta'] = df['Venta'].str.replace(",", ".").astype(float)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True, infer_datetime_format=True)
    # df['Fecha']=df['Fecha'].dt.strftime('%Y-%m-%d')
    df.set_index('Fecha', inplace=True)
    df.drop(['Compra'], axis=1, inplace=True)
    df.rename(columns={'Venta': 'Blue'}, inplace=True)
    df = df.iloc[::-1]
    return df