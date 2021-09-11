from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from haversine import haversine

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

def find_distance(lat1, lon1, lat2, lon2):
    '''
    Return distance btw 2 coordinates in kilometres
    '''
    return haversine((lat1, lon1), (lat2, lon2))
