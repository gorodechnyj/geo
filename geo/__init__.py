from .region.views import getLoc
from .region.models import City, Region
from django.contrib.gis.geos import Point
from urllib import unquote_plus

def getUserLocation(request):
    user_location = getLoc(request)
    lon = float(user_location['coord']['lon'])
    lat = float(user_location['coord']['lat'])
    return Point(lon, lat, srid=4326)

def getUserRegionData(request):
    user_location = getLoc(request)
    return {'city':City.objects.get(name = unquote_plus(user_location['place']['city'])),
            'Region':Region.objects.get(full_name = unquote_plus(user_location['place']['region'])),}