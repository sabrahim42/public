import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely import wkt
import fiona
import os

# def read_file(file_path):
#    _, ext = os.path.splitext(file_path)

#    if ext == '.csv':
#        df = pd.read_csv(file_path)
#    elif ext == '.xlsx':
#        df = pd.read_excel(file_path)
#    else: # assuming it's a spatial file like .shp, .kml, .geojson
#        if ext == '.kml':
#             fiona.supported_drivers['LIBKML'] = 'rw'
#        gdf = gpd.read_file(file_path)

#    return df if 'df' in locals() else gdf

def addGeometryColumnToCoordinateDataFrame(data, campo_longitud, campo_latitud):
    data["geometry"] = [Point(xy) for xy in zip(data[campo_longitud], data[campo_latitud])]

def convertDataFrameToGeoDataFrame(data, campo_geometry, crs = "EPSG:4326"):
    geodata = gpd.GeoDataFrame(data, crs=crs, geometry=campo_geometry)
    return geodata

# Pasar GeoDataFrame a archivos SIG
def writeGeoDataFrameToFile(geodata,output_path,driver=None):
    if output_path.endswith('kml') and driver is None:
        driver = 'LIBKML'
    if driver is not None:
        fiona.supported_drivers[driver] = 'rw'        
    geodata.to_file(output_path, driver=driver)


# ESCRIBIR a archivo de salida csv, excel, kml, shp, etc

# geodata.to_csv(output_path,sep='|',encoding='latin1')
# geodata.to_excel(output_path)