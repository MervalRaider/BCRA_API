#Para consultas y/o sugerencias en twitter: @MervalRaider

import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import requests, json
import os
from Funciones import *
import matplotlib.dates as mdates

#Declaro algunas URLs para hacer el request a la API
urls = {'cer':'https://api.estadisticasbcra.com/cer','infla':'https://api.estadisticasbcra.com/inflacion_mensual_oficial',
        'usd':'https://api.estadisticasbcra.com/usd_of','base':'https://api.estadisticasbcra.com/base',
        'base_usd':'https://api.estadisticasbcra.com/base_usd',
        'leliq':'https://api.estadisticasbcra.com/leliq','reservas':'https://api.estadisticasbcra.com/reservas'}


usd=data_2_col(urls['usd'])
usd.rename(columns={'Valor':'Dolar A3500'},inplace=True)

base= data_2_col(urls['base'])

leliq=data_2_col(urls['leliq'])

#blue=dolar_blue('2018-01-01','2022-06-23')

cer=data_2_col(urls['cer'])
cer.rename(columns={'Valor':'CER'},inplace=True)

reservas=data_2_col(urls['reservas'])

#Concateno los DF que fui obteniendo por separado
monet=pd.concat([base,leliq], axis=1)
monet=pd.concat([monet,reservas], axis=1)
monet.columns=['Base monetaria', 'Leliq','Reservas brutas']
monet=monet['2021-01-01':].interpolate().dropna()
monet['(BM+Leliq)/reservas']=round((monet['Base monetaria']+monet['Leliq'])/monet['Reservas brutas'],2)

#Normalizo base 100 los datos para poder observarlos mejor gráficamente
base100=monet.divide(monet.iloc[0]).mul(100)


a3500=data_2_col(urls['usd'])
a3500['Crawling Peg']=a3500['Valor'].pct_change()
a3500=a3500.reset_index()

for i in range(len(a3500.index)):
    if i == 0:
        continue
    dia = a3500['Fecha'][i] - a3500['Fecha'][i - 1]
    a3500['Crawling Peg'][i] = a3500['Crawling Peg'][i] / (dia.days) * 365

a3500.set_index('Fecha',inplace=True)
a3500=a3500['2021-01-01':]
a3500['Crawling Peg']=a3500['Crawling Peg']*100
a3500['MM semanal']=a3500['Crawling Peg'].rolling(window=5).mean()



plt.style.use('default')
fig ,ax=plt.subplots(figsize=(20,10),ncols=2, nrows=2)
ax[0][0].plot(monet['(BM+Leliq)/reservas'],color='green',linewidth=2)
ax[0][0].fill_between(monet['(BM+Leliq)/reservas'].index,monet['(BM+Leliq)/reservas'],alpha=1,color='green')
ax[0][0].set_ylabel('Dolar según (BM+Leliq)/Rerservas brutas',fontsize=10)

#Si en el gráfico se superponen los labels, se puede solucionar así:
#Solución 1 a la acumulación de labels
#dif=dt.datetime.now().date()-dt.date(2020,1,1)
#plt.xticks(range(1,dif.days,120))

#ax[0][0].xaxis.set_major_locator(plt.MaxNLocator(8))

#Solución 2 a la acumulación de labels
#registros=len(monet.index)
#plt.xticks(range(1,registros,120))
#Solución que me pasaron en el grupo

ax[0][0].grid(alpha=0.5)



ax[1][0].plot(base100[['Base monetaria','Leliq']])
ax[1][0].legend(['Base monetaria','Leliq'])
ax[1][0].set_ylabel('Aumento base monetaria y leliqs base 100',fontsize=10)
ax[1][0].grid(alpha=0.5)
plt.subplots_adjust(wspace=0.1)
ax[1][0].set_title('@MervalRaider',y=0.5,x=0.4,fontsize=40,color='white', bbox=dict(alpha=0.3, color='blue'))

ax[0][1].plot(a3500['MM semanal'],color='green',linewidth=2)
ax[0][1].set_ylabel('Porcentaje de devaluación anual (TNA)',fontsize=10)
ax[0][1].grid(alpha=0.5)
ax[0][1].set_title('Crawling PEG (media móvil semanal)',fontsize=10)

ax[1][1].plot(monet['Reservas brutas'],color='blue')
ax[1][1].set_title('Reservas brutas (en millones de USD)',fontsize=10)
ax[1][1].grid(alpha=0.5)

#Seteo el formato del eje x, para que me lo muestre en el formato de fecha que quiero
formato=mdates.DateFormatter("%m-%y")
ax[0][0].xaxis.set_major_formatter(formato)
ax[0][1].xaxis.set_major_formatter(formato)
ax[1][0].xaxis.set_major_formatter(formato)
ax[1][1].xaxis.set_major_formatter(formato)


plt.show()
