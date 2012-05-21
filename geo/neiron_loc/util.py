# -*- coding: utf-8 -*-
from geo.django_ipgeobase.models import IPGeoBase
import logging
log = logging.getLogger('neiron.geo.neiron_loc.util')

#def set_coords(request, prefix, lat, lon):
#    request.COOKIES[prefix+'_lat'] = lat
#    request.COOKIES[prefix+'_lon'] = lon
    
def del_coords(request, prefix):
    try:
        del request.COOKIES[prefix+'_lat']
        del request.COOKIES[prefix+'_lon']
    except:
        pass
    
def get_radius(request, prefix):
    radius = request.COOKIES.get(prefix+'_radius', 10)
    return radius

#def set_radius(request, prefix, radius):
#    request.COOKIES[prefix+'_radius'] = radius

def get_coords(request, prefix):
    """ Возвращает (lat, lon)
        Берет сначала из сессии, потом по IP, потом по умолчанию
    """
    lat = request.COOKIES.get(prefix + '_lat', None)
    lon = request.COOKIES.get(prefix + '_lon', None)
    try:
        lat = float(lat)
        lon = float(lon)
    except:
        lat = None
        lon = None
        
    if lat and lon:
        log.debug('From cookies: %s %s' % (lat, lon))
        return (lat, lon)
    ip = request.META.get('REMOTE_ADDR', '83.146.95.210')
    log.debug('Got IP: %s' % ip)
    #XXX: Следующая строчка только для локального сервера
    if ip == '127.0.0.1':
        ip = '62.165.38.178'
        
    ipgeobases = IPGeoBase.objects.by_ip(ip)
    if ipgeobases.exists():
        ipgeobase = ipgeobases[0]
        lat = ipgeobase.latitude
        lon = ipgeobase.longitude
#        set_coords(request, prefix, lat, lon)
        log.debug('From ipgeobase: %s %s' % (lat, lon))
        
        if not lat or not lon:
            lon = 61.40258
            lat = 55.159889
        
        return (lat, lon)
    
    # Значения по умолчанию
    lat = 55.159889
    lon = 61.40258
    
    log.debug('From default: %s %s' % (lat, lon))
    
#    set_coords(request, prefix, lat, lon)
    return (lat, lon)
    