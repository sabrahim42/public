import pandas as pd
import geopandas as gpd  
import os

def read_file(file_path,csv_parameters = {}):
   _, ext = os.path.splitext(file_path)

   if ext == '.csv':
       df = pd.read_csv(file_path,**csv_parameters)
   elif ext == '.xlsx':
       df = pd.read_excel(file_path)
   else: # assuming it's a spatial file like .shp, .kml, .geojson
       gdf = gpd.read_file(file_path)

   return df if 'df' in locals() else gdf

def get_dataframes_from_folder(folder_path, ignore_extension = (), csv_parameters = {}):
    folder_dfs = {}
    for file in os.listdir(folder_path):
        if os.path.splitext(file)[1] in ignore_extension:
            continue
        data = read_file(os.path.join(folder_path,file),csv_parameters=csv_parameters)             
        folder_dfs[file] = data
    return folder_dfs