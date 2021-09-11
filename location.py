import math
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable

geolocator = Nominatim(user_agent="main")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def find_house_coordinates(address: str):
    return find_coordinates("Львів, " + address)

def find_coordinates(point: str) -> tuple:
    '''
    Find and return coordinates of place
    >>> find_coordinates('England, UK')
    (52.5310214, -1.2649062)
    >>> find_coordinates("Львів, Козельницька, 2а")
    (49.8170878, 24.023469)
    '''
    try:
        location = geolocator.geocode(point)
        return (location.latitude, location.longitude)
    except (GeocoderUnavailable, AttributeError):
        return None

def find_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    '''
    Find distance between two points by coordinates
    >>> round(find_distance(49.8177029, 24.0237912, 49.2204274, 28.3793954), -2)
    321300.0
    >>> find_distance(5.0, 600.0, 5.0, 600.0)
    0.0
    '''
    radius = 6371e3
    radian_lat1 = lat1 * math.pi/180
    radian_lat2 = lat2 * math.pi/180
    delta_lat = (lat2-lat1) * math.pi/180
    delta_lon = (lon2-lon1) * math.pi/180

    haversine = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
            math.cos(radian_lat1) * math.cos(radian_lat2) * \
            math.sin(delta_lon/2) * math.sin(delta_lon/2)
    haversine = 2 * math.atan2(math.sqrt(haversine), math.sqrt(1-haversine))
    haversine = radius * haversine

    return haversine
