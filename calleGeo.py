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
    callejero.reset_index(inplace=True)

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

def sentido_de_la_cuadra(callejero: gpd.GeoDataFrame):
    # Crear la columna que va a contener si el sentido de la calle es correcto o reverso
    callejero['sentido_correcto'] = True

    # Iterar sobre cada fila del GeoDataFrame usando apply
    def revisar_sentido(fila):
        start, end = fila['geometry'].boundary.geoms  # Obtener punto de inicio de la geometría de la cuadra

        # Obtener las cuadras de la misma calle, excluyendo la actual
        cuadras_calle = callejero.loc[(callejero['nomoficial'] == fila['nomoficial']) & (callejero['id'] != fila['id'])]

        if len(cuadras_calle) > 0:

          # Calcular la distancia desde el punto de inicio de la cuadra actual a las demás cuadras
          cuadras_calle['distancia_temp'] = cuadras_calle['geometry'].distance(start)

          # Obtener la altura inicial de la cuadra más cercana
          altura_cercana = cuadras_calle.loc[cuadras_calle['distancia_temp'].idxmin()]['alt_inicial']

          # Verificar si el sentido de la cuadra es correcto comparando las alturas
          if altura_cercana > fila['alt_inicial']:
              return False

    # Aplicar la función revisar_sentido a cada fila
    callejero['sentido_correcto'] = callejero.apply(revisar_sentido, axis=1)

    return callejero
