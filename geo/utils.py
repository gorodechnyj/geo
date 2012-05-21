# -*- coding: utf-8 -*-
'''
Created on 12.05.2012

@author: gorodechnyj
'''

import json
from django.conf import settings
from urllib2 import urlopen
from urllib import urlencode
from django.contrib.gis.geos import Point

def getPoint(geoobject):
    go = geoobject["Point"]["pos"].split()
    try:
        point = Point(float(go[0]), float(go[1]), srid=4326)
    except:
        point = None
    return point

def get_geocode_from_yandex(city, address):
    city    = unicode(city).encode("utf-8")
    address = unicode(address).encode("utf-8")

    if (city and address):
        params = urlencode({"geocode": city+", "+address, "format": "json",
                                   "key": settings.YANDEX_MAPS_API_KEY})
        url = urlopen("http://geocode-maps.yandex.ru/1.x/?%s" % params)
        geodata = json.loads(url.read())
        #TODO: Проверить все исключения. Написать юнит тесты
        try:
            geoobject = geodata["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            kind = geoobject["metaDataProperty"]["GeocoderMetaData"]["kind"]
            country = geoobject["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]
            region = country.get("AdministrativeArea", None) and country.get("AdministrativeArea").get("AdministrativeAreaName", None)
            city = country.get("AdministrativeArea", None) and country.get("AdministrativeArea").get("Locality", None) and country.get("AdministrativeArea").get("Locality").get("LocalityName", None)
            point = getPoint(geoobject)
            return {"region":region, "city":city, "kind":kind, "point":point}
        except Exception:
            pass
    return {"region":None, "city":None, "kind":None, "point":None}