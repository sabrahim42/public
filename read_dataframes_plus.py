import pandas as pd
import geopandas as gpd  
import os
import csv
import chardet
import fiona

def get_csv_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def get_csv_info(file_path): 
    encoding = get_csv_encoding(file_path) 
    with open(file_path, 'r', encoding = encoding) as f:
        dialect = csv.Sniffer().sniff(f.read())
    return {'delimiter': dialect.delimiter, 'quotechar': dialect.quotechar, 'encoding': encoding}  

def read_file(file_path,csv_parameters = {}) -> pd.DataFrame | gpd.GeoDataFrame | dict[pd.DataFrame]:
   _, ext = os.path.splitext(file_path)

   if ext == '.csv':       
       if csv_parameters == {}:
           csv_parameters = get_csv_info(file_path)
       df = pd.read_csv(file_path,**csv_parameters)
   elif ext == '.xlsx':
       xls = pd.ExcelFile(file_path)
       if len(xls.sheet_names) == 1:
           df = pd.read_excel(xls)
       else:
           df = pd.read_excel(xls,sheet_name=None)  
   else: # assuming it's a spatial file like .shp, .kml, .geojson
       if ext == '.kml':
            fiona.supported_drivers['LIBKML'] = 'rw'
       gdf = gpd.read_file(file_path)

   return df if 'df' in locals() else gdf

def get_dataframes(file_paths: list, csv_parameters = {}):
    dataframes = {}
    for file_path in file_paths:       
        data = read_file(file_path,csv_parameters=csv_parameters) 
        file_name = os.path.basename(file_path)            
        dataframes[file_name] = data
    return dataframes

