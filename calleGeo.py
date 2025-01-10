import pandas as pd
import geopandas as gpd
import numpy as np

def init_callejero_badata():
   # Cargar el callejero de CABA de BAData, con las columnas que se van a usar
  url = 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/jefatura-de-gabinete-de-ministros/calles/callejero.geojson'
  callejero = gpd.read_file(url,columns=['id','nomoficial','alt_izqini', 'alt_izqfin', 'alt_derini','alt_derfin','geometry'])
  callejero = callejero.query('alt_izqini != 0 and  alt_izqfin != 0 and  alt_derini != 0 and alt_derfin != 0')

  # Crear columnas para la altura máxima y mínima por cada cuadra del callejero
  callejero = callejero.assign(alt_inicial = lambda df: [min(x,y) for ix,x,y in df[['alt_izqini','alt_derini']].itertuples()])
  callejero = callejero.assign(alt_final = lambda df: [max(x,y) for ix,x,y in df[['alt_izqfin','alt_derfin']].itertuples()])

  callejero.drop(columns=['alt_izqini', 'alt_izqfin', 'alt_derini','alt_derfin'],inplace=True)

  return callejero


def geolocalizar_con_callejero(fila,calle:str,altura:str, cruce:str,callejero):
  if pd.notnull(fila[cruce]):
    # Disuelvo las lineas de cuadras una sola linea por calle
    callejero = callejero.dissolve(by='nomoficial')

    # Encuentro los registros de la calle principal y del cruce de la direccion
    calle_1 = callejero[callejero['nomoficial'] == fila[calle]]
    calle_2 = callejero[callejero['nomoficial'] == fila[cruce]]

    # Obtengo el punto de interseccion de las geometrias de las calles
    if len(calle_1) == 1 and len(calle_2) == 1:
      return calle_1.iloc[0].geometry.intersection(calle_2.iloc[0].geometry)

  elif pd.notnull(fila[altura]):
    # Buscar el registro correspondiente a la cuadra de la direccion
    cuadra = callejero[(callejero['nomoficial'] == fila[calle])
                        & (callejero['alt_inicial'] <= fila[altura])
                        & (callejero['alt_final'] >= fila[altura])]

    # Obtengo el centroide de la geometria de la cuadra de la direccion
    if len(cuadra) == 1:
      return cuadra.iloc[0].geometry.centroid

    # Calcular las posiciones relativas a la que se encuentra cada direccion en la cuadra
    #posiciones_relativas = geometrias_direcciones.apply(lambda x:(x[altura] - x['alt_inicial'])/(x['alt_final'] - x['alt_inicial']),axis=1)

   # Interpolar los puntos de las direcciones en base a la posicion relativa que tienen en la cuadra
    #geometrias_direcciones['PUNTO_DIRECCION'] = geometrias_direcciones['geometry'].interpolate(posiciones_relativas, normalized = True)


  # Si faltan datos para geolocalizar, devuelvo NaN
  return np.nan
