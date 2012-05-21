# -*- coding: utf-8 -*-
#from sencha.request import SenchaJSONStoreRequest
from django.http import HttpResponse, HttpResponseRedirect
from geo.django_ipgeobase.models import IPGeoBase
from .models import City
from django.db import connection
from urllib import unquote_plus
from django.shortcuts import render_to_response

import urllib
import simplejson

import logging
from django.template.context import RequestContext

logger = logging.getLogger('neiron.region')

class GoogleCityRegion:
    def __init__(self):
        self.city = None
        self.region = None
        self.results = ""
        self.logger = logging.getLogger('neiron.region.GoogleCityRegion')
        
    def parseResults(self, buff):
        self.results = simplejson.loads(buff)
        if self.results['status'] == 'OK':
            results = self.results['results']
            for component in results[0]['address_components']:
                if 'locality' in component['types']:
                    self.city = component['long_name'].replace(u'город ', '')
                    continue
                if 'administrative_area_level_1' in component['types']:
                    self.region = component['long_name']
                    continue
        else:
            self.logger.error('Google Geocoder returned status: %s' % self.results['status'])
        
        
    def requestJSON(self, lat, lng):
        sensor = 'false'
        latlng = str(lat) + ',' + str(lng)
        url = urllib.urlopen('http://maps.googleapis.com/maps/api/geocode/json?language=ru&sensor=%s&latlng=%s' % (sensor, latlng))
        self.parseResults(url.read())
        
#def setUserLocation(request):
#    query = SenchaJSONStoreRequest(request)
#    if 'coord' in query.data:
#        request.session['userLat'] = query.data['coord']['lat']
#        request.session['userLon'] = query.data['coord']['lon']
#    if 'place' in query.data:
#        request.session['userCity'] = query.data['place']['city']
#        request.session['userRegion'] = query.data['place']['region']
#    return HttpResponse('OK')

def setLoc(request, user):
    if 'coord' in user:
        request.session['userLat'] = user['coord']['lat']
        request.session['userLon'] = user['coord']['lon']
        logger.info('Saving lat and lon')
    if 'place' in user:
        request.session['userCity'] = user['place']['city']
        request.session['userRegion'] = user['place']['region']
    
def getCoordsFromIP(request):
    try:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    except:
        ip = request.META['REMOTE_ADDR']
    ipgeobases = IPGeoBase.objects.by_ip(ip)
    if ipgeobases.exists():
        ipgeobase = ipgeobases[0]
        lat = ipgeobase.latitude
        lon = ipgeobase.longitude
    else:
        lat = 55.159889
        lon = 61.40258
        
    content = "var userRegion = {coord: {lat: %s, lon: %s}};" % (lat, lon)
    return HttpResponse(content, mimetype='application/javascript')
    
def getLoc(request, data = {}):    
#    query = SenchaJSONStoreRequest(request)
    logger.info('Entering getUserLocation')
    user = {
            'place': {
                    'city': None,
                    'region': None,
                    },
            'coord': {
                    'lat': None,
                    'lon': None,
                    },
            'pos_place': {
                          'city': None,
                          'region': None,
                          },
            'source': None,
            }
    # Определение пользовательских координат
    # 1. Проверяем сессию
    source = 'session'
    lat = request.session.get('userLat', None)
    lon = request.session.get('userLon', None)
    city = request.session.get('userCity', None)
    region = request.session.get('userRegion', None)
    logger.info('Coords from session: lat = %s; lon = %s; city = %s; region = %s' % (lat, lon, city, region))
    
    # Если в сессии координат нет, то ищем в их запросе (если они были определены, например, через navigator.geolocation)
    # 2. Проверяем переданные координаты
    if lat == None or lon == None:
        source = 'geolocation'
        if 'coord' in data:
            lat = data['coord']['lat']
            lon = data['coord']['lon']
        logger.info('Got coords from query: lat = %s; lon = %s' % (lat, lon))
        
    # Если координаты переданы не были, то:
    # 3. Получаем координаты по IP
    if lat == None or lon == None:
        source = 'IP'
        try:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        except:
            ip = request.META['REMOTE_ADDR']
        ip = '83.146.95.210'
        ipgeobases = IPGeoBase.objects.by_ip(ip)
        if ipgeobases.exists():
            ipgeobase = ipgeobases[0]
            lat = ipgeobase.latitude
            lon = ipgeobase.longitude
        logger.info('Got coords from IP: lat = %s; lon = %s' % (lat, lon))
            
    # Если координаты так и не удалось определить, подставляем значения по умолчанию
    if lat == None or lon == None:
        source = 'default'
        lat = 55.159889
        lon = 61.40258
        
        logger.info('Got default coords: lat = %s; lon = %s' % (lat, lon))
        
    if city and region:
        # Если город и регион определились из куков
        user['place']['city'] = city
        user['place']['region'] = region
        
    user['coord']['lat'] = lat
    user['coord']['lon'] = lon
    # На этом этапе координаты точно есть, определяем город и регион
    if city == None or region == None:
        # Города и региона нет в куках
        gCityRegion = GoogleCityRegion()
        gCityRegion.requestJSON(lat, lon)
        logger.info('From Google Geocoder: city = %s; region = %s' % (gCityRegion.city, gCityRegion.region))
        city = gCityRegion.city
        region = gCityRegion.region
        
    # Если город/регион определить не удалось, подставляем значения по умолчанию
    if city == None or region == None:
        city = u'Челябинск'
        region = u'Челябинская область'
        
    # В pos_place заносим город и регион, вычисленные по координатам
    # если в place данных нет (т.е. они не определились по кукам), то эти данные заносим и в place
    user['pos_place']['city'] = city
    user['pos_place']['region'] = region
    
    if user['place']['city'] == None or user['place']['region'] == None:
        user['place']['city'] = city
        user['place']['region'] = region
        
    user['source'] = source
    
    return user

#def getUserLocation(request):
#    ''' Возвращает координаты пользователя и регион
#    '''
#    query = SenchaJSONStoreRequest(request)
#    user = getLoc(request, query.data)
#        
#    content = simplejson.dumps(user)
#    if query.getCallback(): content = "%s(%s)"%(query.getCallback(), content)
#    
#    return HttpResponse(content, mimetype='application/javascript')

def regionValidate(request):
    ''' Проверяет правильность заполнения формы на странице установки региона
    '''
    logger = logging.getLogger('neiron.region.regionValidate')
    if request.REQUEST.has_key('user_region'):
        cursor = connection.cursor()
        value = request.REQUEST['user_region'].split(',')
        value = [i.strip() for i in value]
        
        if len(value) == 1:
            sql = "SELECT DISTINCT city, region FROM django_ipgeobase_ipgeobase WHERE city = %s"
            cursor.execute(sql, (value[0],))
        else:
            sql = "SELECT DISTINCT city, region FROM django_ipgeobase_ipgeobase WHERE city = %s AND region = %s"
            cursor.execute(sql, (value[0], value[1]))
        
        row = cursor.fetchall()
        if len(row) > 1:
            return HttpResponse(simplejson.dumps({'status': 'AMBIGIOUS'}), content_type="application/javascript; charset=utf-8")
        elif len(row) == 1:
            return HttpResponse(simplejson.dumps({'status': 'OK', 'place': {'city': row[0][0], 'region': row[0][1]}}), content_type="application/javascript; charset=utf-8")
        else:
            return HttpResponse(simplejson.dumps({'status': 'NULL'}), content_type="application/javascript; charset=utf-8")
        
    logger.error('Wrong request format.')
    return HttpResponse('Wrong format')

def regionSubmit(request):
    # Если проводилась ajax-валидация, то заполнены поля city, region, lat, lon:
    if request.POST['city'] and request.POST['region'] and request.POST['lat'] and request.POST['lon']:
        city = request.POST['city']
        region = request.POST['region']
        lat = request.POST['lat']
        lon = request.POST['lon']
    else:
        # проводим валидацию
        response = simplejson.loads(regionValidate(request).content)
        if response['status'] == 'OK':
            city = response['place']['city']
            region = response['place']['region']
            lat = ''
            lon = ''
        else:
            # TODO: обрабатывать ситуацию, когда валидация не прошла
            return HttpResponse('ERROR')
    user = {
            'place': {
                      'city': city,
                      'region': region
                      }
            }
    if lat and lon:
        user['coord'] = {
                      'lat': lat,
                      'lon': lon
                      }
    setLoc(request, user)
    if request.REQUEST.has_key('next'):
        redir = request.REQUEST['next']
    else:
        redir = '/'
    return HttpResponseRedirect(redir)

def regionAjax(request):
    ''' Возвращает список городов, начинающихся с заданных букв
    '''
    logger = logging.getLogger('neiron.region.regionAjax')
    if request.REQUEST.has_key("startsWith"):
        cursor = connection.cursor()
        value = request.REQUEST['startsWith']
        sql = "SELECT DISTINCT city, region FROM django_ipgeobase_ipgeobase WHERE city || ', ' || region ILIKE %s || '%%' ORDER BY city, region"
        cursor.execute(sql, (value,))
        row = cursor.fetchall()
        
        matches = []
        for value in row:
            logger.info("%s, %s" % (value[0], value[1]))
            matches.append({
                            'label': "%s,%s" % (value[0], value[1]),
                            'value': "%s, %s" % (value[0], value[1]),
                            })
        content = {
                   'status': 'OK',
                   'regions': matches,
                   }
            
        return HttpResponse(simplejson.dumps(content), content_type="application/javascript; charset=utf-8")

    logger.error('Wrong request format.')            
    return HttpResponse('Wrong format')
    
def user_region(request):
    region_id = request.session.get('user_region', 999)
    region_object = City.objects.get(id=region_id)
    user_region = u'%s, %s' % (region_object.name, region_object.rid.full_name)
    if 'next' in request.GET:
        next = unicode(unquote_plus(str(request.GET.get('next'))), 'utf-8')
    else:
        next = ''
    return render_to_response('web/user_region.html',
                              {'next': next,
                               'user_region': user_region},
                              RequestContext(request))
 
def user_region_ajax_search(request):
    if request.REQUEST.has_key("startsWith"):
        value = request.REQUEST[u'startsWith']
        results = City.objects.filter(name__istartswith=value)[:10]
        matches = []
        for result in results:
            matches.append({
                            'label': "%s (%s)" % (result.name, result.rid.full_name),
                            'value': "%s, %s" % (result.name, result.rid.full_name),
                            })
        content = {
                   'status': 'OK',
                   'regions': matches,
                   }
            
        return HttpResponse(simplejson.dumps(content), content_type="application/javascript; charset=utf-8")

def user_region_validate(request):
    status = 'OK'
    if request.REQUEST.has_key('user_region'):
        req = request.REQUEST['user_region'].split(', ')
        try:
            if len(req) > 1:
                city = City.objects.get(name__iexact=req[0], rid__full_name__iexact=req[1])
            else:
                city = City.objects.get(name__iexact=req[0])
            request.session['user_region'] = city.id
        except City.DoesNotExist:
            status = 'NULL'
        except City.MultipleObjectsReturned:
            status = 'AMBIGOUS'
    return HttpResponse(simplejson.dumps({'status': status}), content_type="application/javascript; charset=utf-8")

def user_region_get(request):
    region_id = request.session.get('user_region', 999)
    if region_id:
        region_object = City.objects.get(id=region_id)
        city = region_object.name
        region = region_object.rid.name
    else:
        city = 'None'
        region = 'None'
    return HttpResponse(simplejson.dumps({'city': city,
                                          'region': region}), 
                        content_type="application/javascript; charset=utf-8")

def user_region_result(request):
    if request.REQUEST.has_key('user_region'):
        req = request.REQUEST['user_region'].split(', ')
        try:
            if len(req) > 1:
                city = City.objects.get(name=req[0], rid__full_name=req[1])
            else:
                city = City.objects.get(name=req[0])
            request.session['user_region'] = city.id
        except City.DoesNotExist:
            pass
    if request.REQUEST.has_key('next'):
        next = request.REQUEST['next']
    else:
        next = '/'
    return HttpResponseRedirect(next)
