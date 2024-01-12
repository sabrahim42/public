import pandas as pd
import geopandas as gpd  
import os
import pathlib
import csv
import chardet

def get_csv_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def get_csv_info(file_path): 
    encoding = get_csv_encoding(file_path) 
    with open(file_path, 'r', encoding = encoding) as f:
        dialect = csv.Sniffer().sniff(f.read())
    return {'delimiter': dialect.delimiter, 'quotechar': dialect.quotechar, 'encoding': encoding}  

def read_file(file_path,csv_parameters = {}):
   _, ext = os.path.splitext(file_path)

   if ext == '.csv':       
       if csv_parameters == {}:
           csv_parameters = get_csv_info(file_path)
       df = pd.read_csv(file_path,**csv_parameters)
   elif ext == '.xlsx':
       df = pd.read_excel(file_path)
   else: # assuming it's a spatial file like .shp, .kml, .geojson
       gdf = gpd.read_file(file_path)

   return df if 'df' in locals() else gdf

def get_dataframe_file_paths(folder_path,ignore_extension = ()):
    dir = pathlib.Path(folder_path)
    file_paths = [f for f in dir.iterdir() if f.suffix not in ignore_extension]
    return file_paths

def get_dataframes(file_paths: list, csv_parameters = {}):
    dataframes = {}
    for file_path in file_paths:       
        data = read_file(file_path,csv_parameters=csv_parameters) 
        file_name = os.path.basename(file_path)            
        dataframes[file_name] = data
    return dataframes

def get_dataframes_from_folder(folder_path,ignore_extension = (),csv_parameters = {}):
    file_paths = get_dataframe_file_paths(folder_path,ignore_extension = ignore_extension)
    folder_dfs = get_dataframes(file_paths, csv_parameters = csv_parameters)
    return folder_dfs