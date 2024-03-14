import geopandas as gpd
import pandas as pd
import pathlib
from geopy.geocoders import Nominatim 
from geopy.extra.rate_limiter import RateLimiter

def init_geocode(user_agent: str = "alo", reverse: bool = False):
    geolocator = Nominatim(user_agent=user_agent)
    if reverse:
        geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    else:
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    return geocode

def geolocate(data, geocode, campo_direccion):
    new_data = data.copy(deep=True)

    locations = new_data.apply(lambda x: geocode(x[campo_direccion]),axis=1)
    new_data['X'] = locations.apply(lambda x: x.longitude if x is not None else None)
    new_data['Y'] = locations.apply(lambda x: x.latitude if x is not None else None)

    return new_data

def add_address_details(data,geocode,campo_lat,campo_long):
    new_data = data.copy(deep=True)

    locations = new_data.apply(lambda x: geocode((x[campo_lat],x[campo_long])),axis=1)
    
    new_data['ALTURA'] = locations.apply(lambda x: x.raw['address'].get('house_number',None) if x is not None else None)
    new_data['CALLE'] = locations.apply(lambda x: x.raw['address'].get('road',None) if x is not None else None)
    new_data['BARRIO'] = locations.apply(lambda x: x.raw['address'].get('suburb',None) if x is not None else None)
    new_data['COMUNA'] = locations.apply(lambda x: x.raw['address'].get('state_district',None) if x is not None else None)

    return new_data