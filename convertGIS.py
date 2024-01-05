import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely import wkt
import fiona

def addGeometryColumnToCoordinateDataFrame(data, campo_longitud, campo_latitud):
    data["geometry"] = [Point(xy) for xy in zip(data[campo_longitud], data[campo_latitud])]

def convertDataFrameToGeoDataFrame(data, campo_geometry, crs = "EPSG:4326"):
    geodata = gpd.GeoDataFrame(data, crs=crs, geometry=campo_geometry)
    return geodata

# Pasar GeoDataFrame a archivos SIG
def writeGeoDataFrameToFile(geodata,output_path, driver):
    fiona.supported_drivers[driver] = 'rw'
    geodata.to_file(output_path, driver=driver)


# LEER archivo fuente a GeoDataFrame o DataFrame

# data = pd.read_csv(source_path)
# data = pd.read_excel(source_path)
# geodata = gpd.read_file(source_path)

# ESCRIBIR a archivo de salida csv, excel, kml, shp, etc

# geodata.to_csv(output_path,sep='|',encoding='latin1')
# geodata.to_excel(output_path)